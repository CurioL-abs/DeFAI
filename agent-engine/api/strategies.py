from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from models import (
    Strategy, StrategyCreate, StrategyType, StrategyExecution, StrategyExecutionResponse,
    get_db_session
)
from middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Create a new reusable strategy template"""
    try:
        strategy = Strategy(
            name=strategy_data.name,
            description=strategy_data.description,
            strategy_type=strategy_data.strategy_type,
            protocols=strategy_data.protocols,
            config_template=strategy_data.config_template,
            risk_level=strategy_data.risk_level,
            min_investment=strategy_data.min_investment,
            max_investment=strategy_data.max_investment,
            expected_apy=strategy_data.expected_apy,
            rules=strategy_data.rules,
            constraints=strategy_data.constraints,
            created_by=current_user,
            is_public=strategy_data.is_public
        )
        
        await strategy.save(session)
        
        return {
            "id": strategy.id,
            "name": strategy.name,
            "strategy_type": strategy.strategy_type,
            "created_at": strategy.created_at.isoformat(),
            "message": "Strategy created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create strategy: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def list_strategies(
    session: AsyncSession = Depends(get_db_session),
    strategy_type: Optional[StrategyType] = Query(None, description="Filter by strategy type"),
    public_only: bool = Query(False, description="Show only public strategies"),
    limit: int = Query(50, le=100, description="Maximum number of strategies to return")
):
    """List available strategy templates"""
    try:
        if public_only:
            strategies = await Strategy.get_public_strategies(session)
        elif strategy_type:
            strategies = await Strategy.get_by_type(session, strategy_type)
        else:
            # For simplicity, return public strategies by default
            strategies = await Strategy.get_public_strategies(session)
        
        # Apply limit
        strategies = strategies[:limit]
        
        return [
            {
                "id": strategy.id,
                "name": strategy.name,
                "description": strategy.description,
                "strategy_type": strategy.strategy_type,
                "risk_level": strategy.risk_level,
                "expected_apy": strategy.expected_apy,
                "protocols": strategy.protocols,
                "min_investment": strategy.min_investment,
                "max_investment": strategy.max_investment,
                "total_uses": strategy.total_uses,
                "success_rate": strategy.success_rate,
                "average_profit": strategy.average_profit,
                "is_verified": strategy.is_verified,
                "created_at": strategy.created_at.isoformat()
            }
            for strategy in strategies
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list strategies: {str(e)}"
        )

@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get detailed information about a specific strategy"""
    try:
        strategy = await Strategy.get(session, strategy_id)
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "strategy_type": strategy.strategy_type,
            "protocols": strategy.protocols,
            "config_template": strategy.config_template,
            "risk_level": strategy.risk_level,
            "min_investment": strategy.min_investment,
            "max_investment": strategy.max_investment,
            "expected_apy": strategy.expected_apy,
            "rules": strategy.rules,
            "constraints": strategy.constraints,
            "total_uses": strategy.total_uses,
            "average_profit": strategy.average_profit,
            "success_rate": strategy.success_rate,
            "is_public": strategy.is_public,
            "is_verified": strategy.is_verified,
            "created_by": strategy.created_by,
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy: {str(e)}"
        )

@router.get("/executions/recent")
async def get_recent_executions(
    session: AsyncSession = Depends(get_db_session),
    hours: int = Query(24, le=168, description="Number of hours to look back"),
    limit: int = Query(50, le=100, description="Maximum number of executions to return"),
    successful_only: bool = Query(False, description="Show only successful executions")
):
    """Get recent strategy executions across all agents"""
    try:
        executions = await StrategyExecution.get_recent(session, hours, limit)
        
        if successful_only:
            executions = [exec for exec in executions if exec.success]
        
        return [
            {
                "id": execution.id,
                "agent_id": execution.agent_id,
                "strategy_type": execution.strategy_type,
                "protocol": execution.protocol,
                "status": execution.status,
                "start_time": execution.start_time.isoformat(),
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "duration_seconds": execution.duration_seconds,
                "profit": execution.profit,
                "profit_percent": execution.profit_percent,
                "success": execution.success,
                "transaction_ids": execution.transaction_ids
            }
            for execution in executions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent executions: {str(e)}"
        )

@router.get("/executions/{execution_id}")
async def get_execution_details(
    execution_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get detailed information about a specific strategy execution"""
    try:
        execution = await StrategyExecution.get(session, execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )
        
        return {
            "id": execution.id,
            "agent_id": execution.agent_id,
            "strategy_type": execution.strategy_type,
            "protocol": execution.protocol,
            "decision": execution.decision,
            "status": execution.status,
            "start_time": execution.start_time.isoformat(),
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "duration_seconds": execution.duration_seconds,
            "transaction_ids": execution.transaction_ids,
            "gas_fees": execution.gas_fees,
            "input_amount": execution.input_amount,
            "output_amount": execution.output_amount,
            "profit": execution.profit,
            "profit_percent": execution.profit_percent,
            "expected_profit": execution.expected_profit,
            "market_data": execution.market_data,
            "success": execution.success,
            "error_message": execution.error_message,
            "execution_context": execution.execution_context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution details: {str(e)}"
        )

@router.get("/types")
async def get_strategy_types():
    """Get available strategy types and their descriptions"""
    return {
        "strategy_types": [
            {
                "type": StrategyType.SWAP,
                "name": "Token Swap",
                "description": "Simple token swapping using DEX aggregators",
                "risk_level": "Low",
                "protocols": ["jupiter"]
            },
            {
                "type": StrategyType.LENDING,
                "name": "Lending/Borrowing",
                "description": "Deposit tokens to earn yield or borrow for leverage",
                "risk_level": "Medium",
                "protocols": ["marginfi", "solend"]
            },
            {
                "type": StrategyType.LIQUIDITY_PROVISION,
                "name": "Liquidity Provision",
                "description": "Provide liquidity to AMM pools for trading fees",
                "risk_level": "Medium-High",
                "protocols": ["orca", "raydium"]
            },
            {
                "type": StrategyType.YIELD_FARMING,
                "name": "Yield Farming",
                "description": "Stake LP tokens or other assets for additional rewards",
                "risk_level": "High",
                "protocols": ["raydium", "kamino"]
            },
            {
                "type": StrategyType.ARBITRAGE,
                "name": "Arbitrage",
                "description": "Exploit price differences across protocols",
                "risk_level": "Medium",
                "protocols": ["jupiter", "orca", "raydium"]
            },
            {
                "type": StrategyType.MULTI_HOP,
                "name": "Multi-hop Strategy",
                "description": "Complex strategies involving multiple sequential actions",
                "risk_level": "High",
                "protocols": ["multiple"]
            }
        ]
    }

@router.get("/analytics/summary")
async def get_strategy_analytics(
    session: AsyncSession = Depends(get_db_session),
    hours: int = Query(24, le=168, description="Time window for analytics")
):
    """Get analytics summary for all strategy executions"""
    try:
        # Get recent executions
        executions = await StrategyExecution.get_recent(session, hours, 1000)
        
        if not executions:
            return {
                "period_hours": hours,
                "total_executions": 0,
                "successful_executions": 0,
                "success_rate": 0,
                "total_profit": 0,
                "total_volume": 0,
                "average_profit_per_trade": 0,
                "strategy_breakdown": {},
                "protocol_breakdown": {}
            }
        
        # Calculate metrics
        total_executions = len(executions)
        successful_executions = sum(1 for ex in executions if ex.success)
        success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
        total_profit = sum(ex.profit for ex in executions)
        total_volume = sum(ex.input_amount for ex in executions if ex.input_amount)
        avg_profit = total_profit / total_executions if total_executions > 0 else 0
        
        # Strategy type breakdown
        strategy_breakdown = {}
        for execution in executions:
            strategy_type = execution.strategy_type
            if strategy_type not in strategy_breakdown:
                strategy_breakdown[strategy_type] = {
                    "count": 0,
                    "successful": 0,
                    "profit": 0
                }
            strategy_breakdown[strategy_type]["count"] += 1
            if execution.success:
                strategy_breakdown[strategy_type]["successful"] += 1
            strategy_breakdown[strategy_type]["profit"] += execution.profit
        
        # Protocol breakdown
        protocol_breakdown = {}
        for execution in executions:
            if execution.protocol:
                protocol = execution.protocol
                if protocol not in protocol_breakdown:
                    protocol_breakdown[protocol] = {
                        "count": 0,
                        "successful": 0,
                        "profit": 0
                    }
                protocol_breakdown[protocol]["count"] += 1
                if execution.success:
                    protocol_breakdown[protocol]["successful"] += 1
                protocol_breakdown[protocol]["profit"] += execution.profit
        
        return {
            "period_hours": hours,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": round(success_rate, 2),
            "total_profit": round(total_profit, 4),
            "total_volume": round(total_volume, 2),
            "average_profit_per_trade": round(avg_profit, 4),
            "strategy_breakdown": {
                k: {
                    "count": v["count"],
                    "success_rate": round((v["successful"] / v["count"]) * 100, 2),
                    "total_profit": round(v["profit"], 4)
                }
                for k, v in strategy_breakdown.items()
            },
            "protocol_breakdown": {
                k: {
                    "count": v["count"],
                    "success_rate": round((v["successful"] / v["count"]) * 100, 2),
                    "total_profit": round(v["profit"], 4)
                }
                for k, v in protocol_breakdown.items()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )
