from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from models import (
    Agent, AgentCreate, AgentUpdate, AgentResponse, AgentStatus,
    get_db_session, StrategyExecution, AgentPerformance
)
from core.agent_manager import AgentManager
from middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)  # TODO: Replace with actual auth
):
    """Create a new AI agent"""
    try:
        # Create agent instance
        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            strategy_type=agent_data.strategy_type,
            strategy_config=agent_data.strategy_config,
            risk_level=agent_data.risk_level,
            protocols=agent_data.protocols,
            watched_tokens=agent_data.watched_tokens,
            max_investment=agent_data.max_investment,
            min_profit_threshold=agent_data.min_profit_threshold,
            stop_loss_percent=agent_data.stop_loss_percent,
            owner_id=current_user,
            is_public=agent_data.is_public
        )
        
        # Save to database
        await agent.save(session)
        
        # Register with agent manager (this will create wallet, etc.)
        # Note: In production, this should be done asynchronously
        # agent_manager = AgentManager()
        # await agent_manager.create_agent(agent)
        
        return AgentResponse(**agent.to_dict())
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
    status_filter: Optional[AgentStatus] = Query(None, description="Filter by agent status"),
    limit: int = Query(50, le=100, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip")
):
    """List user's agents with optional filtering"""
    try:
        agents = await Agent.get_by_owner(session, current_user)
        
        # Apply status filter if provided
        if status_filter:
            agents = [agent for agent in agents if agent.status == status_filter]
        
        # Apply pagination
        agents = agents[offset:offset + limit]
        
        return [AgentResponse(**agent.to_dict()) for agent in agents]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Get detailed information about a specific agent"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership or public visibility
        if agent.owner_id != current_user and not agent.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return AgentResponse(**agent.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Update an existing agent"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership
        if agent.owner_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update fields that are provided
        update_data = agent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        # Save changes
        await agent.save(session)
        
        return AgentResponse(**agent.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Delete an agent (and stop it if running)"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership
        if agent.owner_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Stop agent if it's running
        if agent.status == AgentStatus.ACTIVE:
            # TODO: Stop agent in agent manager
            await agent.update_status(session, AgentStatus.STOPPED)
        
        # In a real implementation, we'd also:
        # 1. Close all open positions
        # 2. Transfer remaining funds back to owner
        # 3. Clean up agent wallet
        
        # For now, just mark as deleted (soft delete)
        await agent.update_status(session, AgentStatus.STOPPED)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Agent deleted successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )

@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Start an agent (activate autonomous trading)"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership
        if agent.owner_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if agent can be started
        if agent.status not in [AgentStatus.CREATED, AgentStatus.PAUSED, AgentStatus.STOPPED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start agent with status: {agent.status}"
            )
        
        # Validate agent configuration
        if not agent.wallet_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent wallet not configured"
            )
        
        # Update status to active
        await agent.update_status(session, AgentStatus.ACTIVE)
        
        # TODO: Activate agent in agent manager
        # agent_manager = AgentManager()
        # await agent_manager.activate_agent(agent_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Agent started successfully",
                "agent_id": agent_id,
                "status": agent.status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start agent: {str(e)}"
        )

@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Stop an agent (pause autonomous trading)"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership
        if agent.owner_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update status to stopped
        await agent.update_status(session, AgentStatus.STOPPED)
        
        # TODO: Stop agent in agent manager
        # agent_manager = AgentManager()
        # await agent_manager.stop_agent(agent_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Agent stopped successfully",
                "agent_id": agent_id,
                "status": agent.status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop agent: {str(e)}"
        )

@router.post("/{agent_id}/pause")
async def pause_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user)
):
    """Pause an agent (temporarily stop autonomous trading)"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership
        if agent.owner_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Can only pause active agents
        if agent.status != AgentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot pause agent with status: {agent.status}"
            )
        
        # Update status to paused
        await agent.update_status(session, AgentStatus.PAUSED)
        
        # TODO: Pause agent in agent manager
        # agent_manager = AgentManager()
        # await agent_manager.pause_agent(agent_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Agent paused successfully",
                "agent_id": agent_id,
                "status": agent.status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause agent: {str(e)}"
        )

@router.get("/{agent_id}/executions")
async def get_agent_executions(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
    limit: int = Query(50, le=100, description="Maximum number of executions to return"),
    offset: int = Query(0, ge=0, description="Number of executions to skip")
):
    """Get execution history for an agent"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership or public visibility
        if agent.owner_id != current_user and not agent.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get executions
        executions = await StrategyExecution.get_by_agent(session, agent_id, limit + offset)
        
        # Apply pagination
        executions = executions[offset:offset + limit]
        
        return [execution.to_dict() for execution in executions]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get executions: {str(e)}"
        )

@router.get("/{agent_id}/performance")
async def get_agent_performance(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
    days: int = Query(30, le=365, description="Number of days of performance history")
):
    """Get performance metrics for an agent"""
    try:
        agent = await Agent.get(session, agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check ownership or public visibility
        if agent.owner_id != current_user and not agent.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get performance history
        performance_records = await AgentPerformance.get_agent_history(session, agent_id, days)
        
        # Calculate summary statistics
        total_profit = sum(record.total_profit for record in performance_records)
        total_trades = sum(record.trades_count for record in performance_records)
        successful_trades = sum(record.successful_trades for record in performance_records)
        
        avg_success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Best and worst day performance
        daily_profits = [record.total_profit for record in performance_records]
        best_day = max(daily_profits) if daily_profits else 0
        worst_day = min(daily_profits) if daily_profits else 0
        
        performance_summary = {
            "agent_id": agent_id,
            "period_days": days,
            "total_profit": total_profit,
            "total_trades": total_trades,
            "successful_trades": successful_trades,
            "avg_success_rate": avg_success_rate,
            "best_day_profit": best_day,
            "worst_day_profit": worst_day,
            "current_portfolio_value": performance_records[0].portfolio_value if performance_records else 0,
            "daily_records": [record.to_dict() for record in performance_records]
        }
        
        return performance_summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance: {str(e)}"
        )
