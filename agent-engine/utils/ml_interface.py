import logging
import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import numpy as np
from models.strategy import StrategyType, Protocol

logger = logging.getLogger(__name__)

class MLInterface:
    """
    Enhanced ML interface that connects the agent engine to the existing AI service
    Provides real-time strategy decisions based on market data and agent configuration
    """
    
    def __init__(self):
        self.ai_service_url = "http://ai:8001"  # Existing AI service
        self.decision_cache = {}  # Cache recent decisions to avoid repeated calls
        self.cache_ttl = 60  # Cache time-to-live in seconds
    
    async def get_strategy_decision(
        self,
        agent_id: str,
        market_data: Dict[str, Any],
        current_positions: Dict[str, Any],
        agent_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI-driven strategy decision for an agent
        
        Args:
            agent_id: The agent's unique identifier
            market_data: Current market conditions and prices
            current_positions: Agent's current portfolio positions
            agent_config: Agent configuration including risk level, constraints
            
        Returns:
            Dictionary containing strategy decision with type, parameters, and confidence
        """
        try:
            # Check cache first
            cache_key = f"{agent_id}_{hash(str(market_data))}"
            cached_decision = self._get_cached_decision(cache_key)
            if cached_decision:
                logger.info(f"Using cached decision for agent {agent_id}")
                return cached_decision
            
            # Prepare enhanced input for AI service
            ai_input = await self._prepare_ai_input(
                agent_id, market_data, current_positions, agent_config
            )
            
            # Call existing AI service with enhanced data
            raw_decision = await self._call_ai_service(ai_input)
            
            # Post-process and enhance the decision
            enhanced_decision = await self._enhance_decision(
                raw_decision, agent_config, market_data
            )
            
            # Cache the decision
            self._cache_decision(cache_key, enhanced_decision)
            
            logger.info(f"Generated strategy decision for agent {agent_id}: {enhanced_decision.get('strategy_type')}")
            return enhanced_decision
            
        except Exception as e:
            logger.error(f"Failed to get strategy decision: {e}")
            # Return safe default decision
            return self._get_safe_default_decision(agent_config)
    
    async def _prepare_ai_input(
        self,
        agent_id: str,
        market_data: Dict[str, Any],
        current_positions: Dict[str, Any],
        agent_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare comprehensive input for the AI service"""
        
        # Extract key market indicators
        prices = market_data.get('prices', {})
        protocols = market_data.get('protocols', {})
        portfolio = market_data.get('portfolio', {})
        
        # Calculate derived features
        portfolio_value = portfolio.get('total_value_usd', 0)
        sol_balance = portfolio.get('sol_balance', 0)
        
        # Risk assessment based on current positions
        position_risk = self._calculate_position_risk(current_positions, portfolio_value)
        
        # Market volatility indicators
        volatility_score = self._calculate_market_volatility(market_data)
        
        # Opportunity scores for different strategies
        opportunity_scores = await self._calculate_opportunity_scores(protocols, prices)
        
        # Prepare feature vector for ML model (similar to existing AI service input)
        features = {
            "strategy_id": f"agent_{agent_id}_{datetime.utcnow().isoformat()}",
            
            # Market features
            "market_volatility": volatility_score,
            "sol_price": prices.get("So11111111111111111111111111111111111111112", 0),
            "usdc_price": prices.get("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 1),
            
            # Portfolio features
            "portfolio_value": portfolio_value,
            "sol_balance": sol_balance,
            "position_count": len(current_positions),
            "position_risk": position_risk,
            
            # Agent configuration
            "risk_tolerance": self._risk_level_to_score(agent_config.get('risk_level', 'medium')),
            "max_investment": agent_config.get('max_investment', 1000),
            "min_profit_threshold": agent_config.get('min_profit_threshold', 0.01),
            
            # Protocol opportunities
            "lending_apy": opportunity_scores.get('lending', 0),
            "lp_rewards": opportunity_scores.get('liquidity', 0),
            "farm_rewards": opportunity_scores.get('farming', 0),
            
            # Additional context
            "protocols_available": list(protocols.keys()),
            "watched_tokens": agent_config.get('watched_tokens', []),
            "current_positions": current_positions,
            
            # Time-based features
            "hour_of_day": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday(),
        }
        
        return features
    
    async def _call_ai_service(self, ai_input: Dict[str, Any]) -> Dict[str, Any]:
        """Call the existing AI service for prediction"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ai_service_url}/predict",
                    json={"strategy_id": ai_input["strategy_id"]},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Enhance with our feature data
                    result["input_features"] = ai_input
                    result["timestamp"] = datetime.utcnow().isoformat()
                    
                    return result
                else:
                    logger.error(f"AI service returned {response.status_code}: {response.text}")
                    return {"pred": 0.005, "strategy_id": ai_input["strategy_id"]}  # Default safe response
                    
        except Exception as e:
            logger.error(f"Failed to call AI service: {e}")
            return {"pred": 0.005, "strategy_id": ai_input["strategy_id"]}  # Default safe response
    
    async def _enhance_decision(
        self,
        raw_decision: Dict[str, Any],
        agent_config: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance raw AI prediction into actionable strategy decision"""
        
        predicted_yield = raw_decision.get('pred', 0.005)
        input_features = raw_decision.get('input_features', {})
        
        # Determine strategy type based on ML prediction and market conditions
        strategy_type, strategy_params = await self._determine_strategy_type(
            predicted_yield, input_features, market_data, agent_config
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(predicted_yield, input_features)
        
        # Risk assessment
        risk_score = self._assess_strategy_risk(strategy_type, strategy_params, agent_config)
        
        # Determine execution timing
        execution_timing = self._determine_execution_timing(predicted_yield, confidence, risk_score)
        
        enhanced_decision = {
            # Core decision
            "strategy_type": strategy_type,
            "predicted_yield": predicted_yield,
            "confidence": confidence,
            "risk_score": risk_score,
            
            # Strategy parameters (specific to strategy type)
            **strategy_params,
            
            # Execution control
            "should_execute": self._should_execute_strategy(predicted_yield, confidence, risk_score, agent_config),
            "next_check_minutes": execution_timing,
            "max_retry_attempts": 3,
            
            # Metadata
            "decision_timestamp": datetime.utcnow().isoformat(),
            "ml_model_version": "v1.0",
            "input_features_hash": hash(str(input_features)),
            
            # Safety constraints
            "constraints": {
                "max_amount": min(
                    agent_config.get('max_investment', 1000) * 0.1,  # Max 10% of max investment per trade
                    input_features.get('portfolio_value', 0) * 0.2  # Max 20% of current portfolio
                ),
                "min_expected_profit": agent_config.get('min_profit_threshold', 0.01),
                "stop_loss_threshold": agent_config.get('stop_loss_percent', 0.1),
            }
        }
        
        logger.info(f"Enhanced decision: {strategy_type} with {confidence:.2f} confidence")
        return enhanced_decision
    
    async def _determine_strategy_type(
        self,
        predicted_yield: float,
        features: Dict[str, Any],
        market_data: Dict[str, Any],
        agent_config: Dict[str, Any]
    ) -> tuple[StrategyType, Dict[str, Any]]:
        """Determine the best strategy type and parameters based on ML prediction and context"""
        
        portfolio_value = features.get('portfolio_value', 0)
        sol_balance = features.get('sol_balance', 0)
        risk_tolerance = features.get('risk_tolerance', 0.5)
        protocols = market_data.get('protocols', {})
        
        # Strategy selection logic based on ML prediction and market conditions
        if predicted_yield > 0.05 and risk_tolerance > 0.7:  # High yield prediction + high risk tolerance
            # Multi-hop arbitrage strategy
            return StrategyType.MULTI_HOP, {
                "steps": [
                    {
                        "strategy_type": StrategyType.SWAP,
                        "from_token": "So11111111111111111111111111111111111111112",  # SOL
                        "to_token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                        "amount": int(sol_balance * 0.5 * 1e9),  # Convert 50% SOL to lamports
                        "slippage": 0.01
                    },
                    {
                        "strategy_type": StrategyType.LENDING,
                        "action": "deposit",
                        "token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                        "protocol": Protocol.MARGINFI,
                        "amount": "auto"  # Use output from previous step
                    }
                ]
            }
            
        elif predicted_yield > 0.02 and sol_balance > 5:  # Medium yield prediction + sufficient SOL
            # Yield farming strategy
            return StrategyType.YIELD_FARMING, {
                "action": "stake",
                "farm_id": "RAY-SOL",
                "token": "So11111111111111111111111111111111111111112",  # SOL
                "amount": int(sol_balance * 0.3 * 1e9),  # Stake 30% of SOL
                "protocol": Protocol.RAYDIUM,
                "expected_apy": predicted_yield * 365  # Annualize the prediction
            }
            
        elif predicted_yield > 0.01 and portfolio_value > 100:  # Conservative yield + sufficient portfolio
            # Lending strategy
            return StrategyType.LENDING, {
                "action": "deposit",
                "token": "So11111111111111111111111111111111111111112",  # SOL
                "amount": int(min(sol_balance * 0.4, portfolio_value * 0.2) * 1e9),  # Conservative amount
                "protocol": Protocol.MARGINFI
            }
            
        elif sol_balance > 1 and len(market_data.get('prices', {})) >= 2:  # Basic swap opportunity
            # Simple swap strategy
            return StrategyType.SWAP, {
                "from_token": "So11111111111111111111111111111111111111112",  # SOL
                "to_token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "amount": int(sol_balance * 0.1 * 1e9),  # Convert 10% of SOL
                "slippage": 0.005,  # 0.5% slippage
                "reason": "portfolio_rebalancing"
            }
            
        else:
            # Hold/no action
            return StrategyType.SWAP, {
                "action": "hold",
                "reason": "insufficient_opportunity",
                "next_evaluation": 30  # Check again in 30 minutes
            }
    
    def _calculate_position_risk(self, positions: Dict[str, Any], portfolio_value: float) -> float:
        """Calculate risk score based on position concentration"""
        if not positions or portfolio_value <= 0:
            return 0.0
            
        # Calculate concentration risk (0-1 scale)
        largest_position = max(positions.values()) if positions else 0
        concentration = largest_position / portfolio_value if portfolio_value > 0 else 0
        
        return min(concentration * 2, 1.0)  # Scale to 0-1, cap at 1
    
    def _calculate_market_volatility(self, market_data: Dict[str, Any]) -> float:
        """Calculate market volatility score (simplified)"""
        # In a real implementation, this would analyze price history
        # For now, return a mock volatility score
        return 0.3  # Medium volatility
    
    async def _calculate_opportunity_scores(
        self, 
        protocols: Dict[str, Any], 
        prices: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate opportunity scores for different strategy types"""
        scores = {
            'lending': 0.0,
            'liquidity': 0.0,
            'farming': 0.0,
            'arbitrage': 0.0
        }
        
        # Lending opportunities
        if 'marginfi' in protocols:
            marginfi_data = protocols['marginfi']
            lending_rates = marginfi_data.get('lending_rates', {})
            scores['lending'] = max(lending_rates.values()) if lending_rates else 0.05
        
        # Liquidity provision opportunities
        if 'orca' in protocols:
            orca_data = protocols['orca']
            pools = orca_data.get('pools', {})
            if pools:
                scores['liquidity'] = max(pool.get('apr', 0) for pool in pools.values())
        
        # Yield farming opportunities
        if 'raydium' in protocols:
            raydium_data = protocols['raydium']
            farms = raydium_data.get('farms', {})
            if farms:
                scores['farming'] = max(farm.get('apy', 0) for farm in farms.values())
        
        return scores
    
    def _risk_level_to_score(self, risk_level: str) -> float:
        """Convert risk level string to numeric score"""
        mapping = {
            'low': 0.2,
            'medium': 0.5, 
            'high': 0.8
        }
        return mapping.get(risk_level.lower(), 0.5)
    
    def _calculate_confidence(self, predicted_yield: float, features: Dict[str, Any]) -> float:
        """Calculate confidence score for the prediction"""
        # Confidence based on prediction magnitude and feature quality
        base_confidence = min(predicted_yield * 10, 0.8)  # Higher yields = higher confidence, cap at 0.8
        
        # Adjust based on data quality
        if features.get('portfolio_value', 0) > 100:
            base_confidence += 0.1
        if len(features.get('protocols_available', [])) >= 3:
            base_confidence += 0.1
            
        return min(base_confidence, 0.95)  # Cap confidence at 95%
    
    def _assess_strategy_risk(
        self, 
        strategy_type: StrategyType, 
        params: Dict[str, Any], 
        agent_config: Dict[str, Any]
    ) -> float:
        """Assess risk level of the proposed strategy"""
        base_risk = {
            StrategyType.SWAP: 0.2,
            StrategyType.LENDING: 0.3,
            StrategyType.LIQUIDITY_PROVISION: 0.5,
            StrategyType.YIELD_FARMING: 0.6,
            StrategyType.ARBITRAGE: 0.7,
            StrategyType.MULTI_HOP: 0.8,
        }.get(strategy_type, 0.5)
        
        # Adjust based on amount
        amount_risk = min(params.get('amount', 0) / agent_config.get('max_investment', 1000), 0.3)
        
        return min(base_risk + amount_risk, 1.0)
    
    def _determine_execution_timing(self, predicted_yield: float, confidence: float, risk_score: float) -> int:
        """Determine when to check again (in minutes)"""
        if predicted_yield > 0.05 and confidence > 0.8:
            return 1  # High opportunity - check very frequently
        elif predicted_yield > 0.02 and confidence > 0.6:
            return 5  # Medium opportunity - check frequently
        elif predicted_yield > 0.01:
            return 15  # Low opportunity - check occasionally
        else:
            return 30  # No opportunity - check infrequently
    
    def _should_execute_strategy(
        self,
        predicted_yield: float,
        confidence: float,
        risk_score: float,
        agent_config: Dict[str, Any]
    ) -> bool:
        """Determine if strategy should be executed based on multiple factors"""
        min_yield = agent_config.get('min_profit_threshold', 0.01)
        risk_tolerance = self._risk_level_to_score(agent_config.get('risk_level', 'medium'))
        
        # Must meet minimum yield threshold
        if predicted_yield < min_yield:
            return False
        
        # Must have sufficient confidence
        if confidence < 0.5:
            return False
            
        # Risk must be acceptable
        if risk_score > risk_tolerance + 0.2:  # Allow slight risk tolerance breach
            return False
            
        return True
    
    def _get_safe_default_decision(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Return a safe default decision when ML service fails"""
        return {
            "strategy_type": StrategyType.SWAP,
            "action": "hold",
            "reason": "ml_service_unavailable",
            "predicted_yield": 0.0,
            "confidence": 0.0,
            "risk_score": 0.0,
            "should_execute": False,
            "next_check_minutes": 60,  # Wait longer before retrying
            "decision_timestamp": datetime.utcnow().isoformat(),
        }
    
    def _get_cached_decision(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached decision if still valid"""
        if cache_key in self.decision_cache:
            cached_data = self.decision_cache[cache_key]
            if datetime.utcnow().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['decision']
        return None
    
    def _cache_decision(self, cache_key: str, decision: Dict[str, Any]):
        """Cache a decision for future use"""
        self.decision_cache[cache_key] = {
            'decision': decision,
            'timestamp': datetime.utcnow().timestamp()
        }
        
        # Cleanup old cache entries
        current_time = datetime.utcnow().timestamp()
        expired_keys = [
            k for k, v in self.decision_cache.items() 
            if current_time - v['timestamp'] > self.cache_ttl
        ]
        for key in expired_keys:
            del self.decision_cache[key]
