import logging
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import json

from models.strategy import StrategyExecution, StrategyType, Protocol
from core.solana_client import SolanaClientManager

logger = logging.getLogger(__name__)

class StrategyEngine:
    """
    Handles strategy execution based on ML decisions
    Translates high-level strategy decisions into Solana transactions
    """
    
    def __init__(self):
        self.solana_client = SolanaClientManager()
        self.strategy_registry = {}
        self._register_strategies()
        
    def _register_strategies(self):
        """Register available strategies"""
        self.strategy_registry = {
            StrategyType.SWAP: self._execute_swap_strategy,
            StrategyType.LENDING: self._execute_lending_strategy,
            StrategyType.LIQUIDITY_PROVISION: self._execute_liquidity_strategy,
            StrategyType.YIELD_FARMING: self._execute_yield_farming_strategy,
            StrategyType.MULTI_HOP: self._execute_multi_hop_strategy,
        }
        
    async def execute_strategy(self, agent_id: str, decision: Dict, market_data: Dict) -> Dict:
        """
        Execute a strategy based on ML decision
        
        Args:
            agent_id: The agent's identifier
            decision: ML-generated decision with strategy type and parameters
            market_data: Current market data
            
        Returns:
            Dict with execution results (success, txids, profit, etc)
        """
        try:
            strategy_type = decision.get('strategy_type')
            if not strategy_type or strategy_type not in self.strategy_registry:
                logger.error(f"Unknown strategy type: {strategy_type}")
                return {'success': False, 'error': 'Unknown strategy type'}
                
            # Get strategy executor function
            strategy_executor = self.strategy_registry[strategy_type]
            
            # Execute strategy
            execution_start = datetime.utcnow()
            result = await strategy_executor(agent_id, decision, market_data)
            execution_end = datetime.utcnow()
            
            # Record execution in database
            execution = StrategyExecution(
                agent_id=agent_id,
                strategy_type=strategy_type,
                decision=decision,
                result=result,
                start_time=execution_start,
                end_time=execution_end,
                profit=result.get('profit', 0),
                success=result.get('success', False)
            )
            await execution.save()  # Assume we have DB model
            
            return result
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'profit': 0
            }
    
    async def _execute_swap_strategy(self, agent_id: str, decision: Dict, market_data: Dict) -> Dict:
        """Execute token swap using Jupiter aggregator"""
        try:
            from_token = decision.get('from_token')
            to_token = decision.get('to_token')
            amount = decision.get('amount')
            slippage = decision.get('slippage', 0.005)  # Default 0.5%
            
            # Validate decision parameters
            if not all([from_token, to_token, amount]):
                return {'success': False, 'error': 'Missing required parameters'}
                
            # Get best route from Jupiter
            route = await self.solana_client.get_jupiter_route(
                input_mint=from_token,
                output_mint=to_token,
                amount=amount,
                slippage=slippage
            )
            
            if not route:
                return {'success': False, 'error': 'No swap route found'}
                
            # Execute swap
            tx_result = await self.solana_client.execute_jupiter_swap(
                agent_id=agent_id,
                route=route
            )
            
            # Calculate profit (if any)
            profit_info = await self._calculate_swap_profit(
                from_token, to_token, amount, tx_result.get('output_amount', 0),
                market_data
            )
            
            return {
                'success': tx_result.get('success', False),
                'txid': tx_result.get('txid'),
                'input_amount': amount,
                'output_amount': tx_result.get('output_amount'),
                'profit': profit_info.get('profit', 0),
                'profit_percent': profit_info.get('profit_percent', 0)
            }
                
        except Exception as e:
            logger.error(f"Swap execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_lending_strategy(self, agent_id: str, decision: Dict, market_data: Dict) -> Dict:
        """Execute lending/borrowing strategy on Marginfi or similar protocol"""
        try:
            action = decision.get('action')  # 'deposit', 'withdraw', 'borrow', 'repay'
            token = decision.get('token')
            amount = decision.get('amount')
            protocol = decision.get('protocol', Protocol.MARGINFI)
            
            # Validate decision parameters
            if not all([action, token, amount]):
                return {'success': False, 'error': 'Missing required parameters'}
                
            # Execute lending action
            tx_result = await self.solana_client.execute_lending_action(
                agent_id=agent_id,
                protocol=protocol,
                action=action,
                token=token,
                amount=amount
            )
            
            return {
                'success': tx_result.get('success', False),
                'txid': tx_result.get('txid'),
                'token': token,
                'amount': amount,
                'protocol': protocol,
                'action': action
            }
                
        except Exception as e:
            logger.error(f"Lending execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_liquidity_strategy(self, agent_id: str, decision: Dict, market_data: Dict) -> Dict:
        """Execute liquidity provision on Orca or similar AMM"""
        try:
            action = decision.get('action')  # 'add', 'remove'
            pool_id = decision.get('pool_id')
            token_a = decision.get('token_a')
            token_b = decision.get('token_b')
            amount_a = decision.get('amount_a', 0)
            amount_b = decision.get('amount_b', 0)
            protocol = decision.get('protocol', Protocol.ORCA)
            
            # Validate decision parameters
            if not all([action, pool_id]) or (action == 'add' and not all([token_a, token_b])):
                return {'success': False, 'error': 'Missing required parameters'}
                
            # Execute liquidity action
            tx_result = await self.solana_client.execute_liquidity_action(
                agent_id=agent_id,
                protocol=protocol,
                action=action,
                pool_id=pool_id,
                token_a=token_a,
                token_b=token_b,
                amount_a=amount_a,
                amount_b=amount_b
            )
            
            return {
                'success': tx_result.get('success', False),
                'txid': tx_result.get('txid'),
                'pool_id': pool_id,
                'protocol': protocol,
                'action': action
            }
                
        except Exception as e:
            logger.error(f"Liquidity execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_yield_farming_strategy(self, agent_id: str, decision: Dict, market_data: Dict) -> Dict:
        """Execute yield farming strategy (stake, unstake, harvest)"""
        try:
            action = decision.get('action')  # 'stake', 'unstake', 'harvest'
            farm_id = decision.get('farm_id')
            token = decision.get('token')
            amount = decision.get('amount', 0)  # Optional for harvest
            protocol = decision.get('protocol', Protocol.RAYDIUM)
            
            # Validate decision parameters
            if not all([action, farm_id]):
                return {'success': False, 'error': 'Missing required parameters'}
                
            # For stake/unstake, amount and token are required
            if action in ['stake', 'unstake'] and not all([token, amount]):
                return {'success': False, 'error': 'Missing token or amount for stake/unstake'}
                
            # Execute yield farming action
            tx_result = await self.solana_client.execute_yield_farm_action(
                agent_id=agent_id,
                protocol=protocol,
                action=action,
                farm_id=farm_id,
                token=token,
                amount=amount
            )
            
            return {
                'success': tx_result.get('success', False),
                'txid': tx_result.get('txid'),
                'farm_id': farm_id,
                'protocol': protocol,
                'action': action,
                'rewards': tx_result.get('rewards', 0) if action == 'harvest' else 0
            }
                
        except Exception as e:
            logger.error(f"Yield farming execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_multi_hop_strategy(self, agent_id: str, decision: Dict, market_data: Dict) -> Dict:
        """Execute multi-step strategy (sequence of actions)"""
        try:
            steps = decision.get('steps', [])
            if not steps:
                return {'success': False, 'error': 'No steps provided for multi-hop strategy'}
                
            results = []
            total_profit = 0
            all_successful = True
            
            # Execute each step sequentially
            for step in steps:
                step_type = step.get('strategy_type')
                if not step_type or step_type not in self.strategy_registry:
                    logger.error(f"Unknown strategy type in multi-hop: {step_type}")
                    all_successful = False
                    break
                
                # Get strategy executor for this step
                step_executor = self.strategy_registry[step_type]
                
                # Execute step
                step_result = await step_executor(agent_id, step, market_data)
                results.append(step_result)
                
                # If step failed, abort sequence
                if not step_result.get('success', False):
                    all_successful = False
                    break
                
                # Add to total profit
                total_profit += step_result.get('profit', 0)
                
                # Update market data if needed for next step
                # TODO: Consider refreshing market data between steps
            
            return {
                'success': all_successful,
                'steps_results': results,
                'completed_steps': len(results),
                'total_steps': len(steps),
                'profit': total_profit
            }
                
        except Exception as e:
            logger.error(f"Multi-hop execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close_position(self, agent_id: str, position_id: str) -> Dict:
        """Close a specific position"""
        try:
            # TODO: Implement position closing logic based on position type
            return {'success': True, 'position_id': position_id}
        except Exception as e:
            logger.error(f"Failed to close position {position_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_swap_profit(self, from_token, to_token, input_amount, output_amount, market_data) -> Dict:
        """Calculate profit from a swap transaction"""
        try:
            # This is a simplified calculation
            # In a real implementation, we would consider market prices,
            # token values in USD, and opportunity costs
            
            input_price = market_data.get('prices', {}).get(from_token, 0)
            output_price = market_data.get('prices', {}).get(to_token, 0)
            
            if not input_price or not output_price:
                return {'profit': 0, 'profit_percent': 0}
                
            input_value = input_amount * input_price
            output_value = output_amount * output_price
            
            profit = output_value - input_value
            profit_percent = (profit / input_value) * 100 if input_value else 0
            
            return {
                'profit': profit,
                'profit_percent': profit_percent
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate swap profit: {e}")
            return {'profit': 0, 'profit_percent': 0}
