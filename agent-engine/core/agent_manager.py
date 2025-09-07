from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from models.agent import Agent, AgentStatus
from models.strategy import StrategyExecution
from core.solana_client import SolanaClientManager
from core.strategy_engine import StrategyEngine
from utils.ml_interface import MLInterface

logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Current state of an AI agent"""
    agent_id: str
    status: AgentStatus
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    total_profit: float = 0.0
    current_positions: Dict = None
    
    def __post_init__(self):
        if self.current_positions is None:
            self.current_positions = {}

class AgentManager:
    """Manages lifecycle and execution of AI agents"""
    
    def __init__(self):
        self.active_agents: Dict[str, AgentState] = {}
        self.solana_client = SolanaClientManager()
        self.strategy_engine = StrategyEngine()
        self.ml_interface = MLInterface()
        self.running = False
        
    async def initialize(self):
        """Initialize the agent manager"""
        await self.solana_client.initialize()
        logger.info("Agent Manager initialized")
    
    async def create_agent(self, agent: Agent) -> AgentState:
        """Create and register a new AI agent"""
        try:
            # Create agent wallet using account abstraction
            wallet_keypair = await self.solana_client.create_agent_wallet(agent.id)
            
            # Initialize agent state
            agent_state = AgentState(
                agent_id=agent.id,
                status=AgentStatus.CREATED,
                next_execution=datetime.utcnow() + timedelta(minutes=1)
            )
            
            self.active_agents[agent.id] = agent_state
            
            # Update agent with wallet info
            agent.wallet_address = str(wallet_keypair.pubkey())
            await agent.save()  # Assume we have DB persistence
            
            logger.info(f"Created agent {agent.id} with wallet {agent.wallet_address}")
            return agent_state
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent.id}: {e}")
            raise
    
    async def activate_agent(self, agent_id: str) -> bool:
        """Activate an agent for autonomous execution"""
        if agent_id not in self.active_agents:
            logger.error(f"Agent {agent_id} not found")
            return False
            
        agent_state = self.active_agents[agent_id]
        agent_state.status = AgentStatus.ACTIVE
        agent_state.next_execution = datetime.utcnow() + timedelta(minutes=1)
        
        logger.info(f"Activated agent {agent_id}")
        return True
    
    async def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent's execution"""
        if agent_id not in self.active_agents:
            return False
            
        self.active_agents[agent_id].status = AgentStatus.PAUSED
        logger.info(f"Paused agent {agent_id}")
        return True
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent and close positions"""
        if agent_id not in self.active_agents:
            return False
            
        agent_state = self.active_agents[agent_id]
        
        # Close all positions
        await self._close_all_positions(agent_id)
        
        agent_state.status = AgentStatus.STOPPED
        logger.info(f"Stopped agent {agent_id}")
        return True
    
    async def run_agent_loop(self):
        """Main execution loop for all agents"""
        self.running = True
        logger.info("Starting agent execution loop")
        
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                # Check each active agent
                for agent_id, agent_state in self.active_agents.items():
                    if (agent_state.status == AgentStatus.ACTIVE and 
                        agent_state.next_execution and 
                        current_time >= agent_state.next_execution):
                        
                        # Execute agent strategy
                        await self._execute_agent_strategy(agent_id)
                
                # Wait before next check
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in agent loop: {e}")
                await asyncio.sleep(30)
    
    async def _execute_agent_strategy(self, agent_id: str):
        """Execute strategy for a specific agent"""
        try:
            agent_state = self.active_agents[agent_id]
            logger.info(f"Executing strategy for agent {agent_id}")
            
            # Get agent configuration
            agent = await Agent.get(agent_id)  # Assume DB model exists
            
            # Gather market data
            market_data = await self._gather_market_data(agent)
            
            # Get ML prediction/decision
            ml_decision = await self.ml_interface.get_strategy_decision(
                agent_id=agent_id,
                market_data=market_data,
                current_positions=agent_state.current_positions,
                agent_config=agent.strategy_config
            )
            
            # Execute strategy based on ML decision
            execution_result = await self.strategy_engine.execute_strategy(
                agent_id=agent_id,
                decision=ml_decision,
                market_data=market_data
            )
            
            # Update agent state
            agent_state.last_execution = datetime.utcnow()
            agent_state.execution_count += 1
            agent_state.total_profit += execution_result.get('profit', 0)
            
            # Schedule next execution (dynamic based on market conditions)
            next_delay_minutes = ml_decision.get('next_check_minutes', 5)
            agent_state.next_execution = datetime.utcnow() + timedelta(minutes=next_delay_minutes)
            
            logger.info(f"Agent {agent_id} executed successfully. Next execution: {agent_state.next_execution}")
            
        except Exception as e:
            logger.error(f"Failed to execute strategy for agent {agent_id}: {e}")
            # Set longer delay on error
            agent_state = self.active_agents[agent_id]
            agent_state.next_execution = datetime.utcnow() + timedelta(minutes=30)
    
    async def _gather_market_data(self, agent: Agent) -> Dict:
        """Gather relevant market data for the agent"""
        try:
            # Get prices from Pyth
            token_prices = await self.solana_client.get_token_prices(agent.watched_tokens)
            
            # Get DeFi protocol data
            protocol_data = await self.solana_client.get_protocol_data(agent.protocols)
            
            # Get portfolio data
            portfolio_data = await self.solana_client.get_portfolio_data(agent.wallet_address)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'prices': token_prices,
                'protocols': protocol_data,
                'portfolio': portfolio_data,
                'market_conditions': await self._assess_market_conditions()
            }
            
        except Exception as e:
            logger.error(f"Failed to gather market data: {e}")
            return {}
    
    async def _assess_market_conditions(self) -> Dict:
        """Assess overall market conditions"""
        # TODO: Implement market sentiment analysis
        return {
            'volatility': 'medium',
            'trend': 'neutral',
            'risk_level': 'moderate'
        }
    
    async def _close_all_positions(self, agent_id: str):
        """Close all positions for an agent"""
        try:
            agent_state = self.active_agents[agent_id]
            
            for position_id, position_data in agent_state.current_positions.items():
                await self.strategy_engine.close_position(agent_id, position_id)
            
            agent_state.current_positions = {}
            logger.info(f"Closed all positions for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to close positions for agent {agent_id}: {e}")
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentState]:
        """Get current status of an agent"""
        return self.active_agents.get(agent_id)
    
    def get_all_agents_status(self) -> Dict[str, AgentState]:
        """Get status of all agents"""
        return self.active_agents.copy()
    
    async def stop(self):
        """Stop the agent manager"""
        self.running = False
        
        # Stop all agents gracefully
        for agent_id in list(self.active_agents.keys()):
            await self.stop_agent(agent_id)
        
        logger.info("Agent Manager stopped")
