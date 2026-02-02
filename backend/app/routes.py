from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import httpx

from .schemas import (
    StrategyCreate,
    StrategyResponse,
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    TransactionResponse,
    PerformanceResponse,
    PerformanceSummary,
)
from .db import get_db_session
from .wallet_auth import get_current_user
from .models import User, AgentStatus
from .repositories import (
    AgentRepository,
    StrategyRepository,
    TransactionRepository,
    PerformanceRepository,
)

router = APIRouter()


# --- Agent endpoints ---


@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    data: AgentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.create(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        risk_tolerance=data.risk_tolerance,
        max_position_size=data.max_position_size,
    )
    return agent


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    return await repo.get_by_user(current_user.id)


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return agent

    updated = await repo.update(agent_id, **updates)
    return updated


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    await repo.delete(agent_id)
    return {"message": "Agent deleted"}


@router.post("/agents/{agent_id}/start")
async def start_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    await repo.update_status(agent_id, AgentStatus.ACTIVE)
    return {"message": "Agent started", "status": "active"}


@router.post("/agents/{agent_id}/stop")
async def stop_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    await repo.update_status(agent_id, AgentStatus.STOPPED)
    return {"message": "Agent stopped", "status": "stopped"}


@router.post("/agents/{agent_id}/pause")
async def pause_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = AgentRepository(session)
    agent = await repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    await repo.update_status(agent_id, AgentStatus.PAUSED)
    return {"message": "Agent paused", "status": "paused"}


# --- Transaction endpoints ---


@router.get("/agents/{agent_id}/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    agent_id: int,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    agent_repo = AgentRepository(session)
    agent = await agent_repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    tx_repo = TransactionRepository(session)
    return await tx_repo.get_by_agent(agent_id, limit=limit, offset=offset)


# --- Performance endpoints ---


@router.get("/agents/{agent_id}/performance", response_model=List[PerformanceResponse])
async def list_performance(
    agent_id: int,
    days: int = Query(default=30, le=365),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    agent_repo = AgentRepository(session)
    agent = await agent_repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    perf_repo = PerformanceRepository(session)
    return await perf_repo.get_by_agent(agent_id, limit=days)


@router.get("/agents/{agent_id}/performance/summary", response_model=PerformanceSummary)
async def get_performance_summary(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    agent_repo = AgentRepository(session)
    agent = await agent_repo.get_by_id(agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Agent not found")

    perf_repo = PerformanceRepository(session)
    return await perf_repo.get_summary(agent_id)


# --- Strategy prediction endpoint ---


@router.post("/strategies", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_user),
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ai:8001/predict", json={"strategy_id": strategy.name}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI service error")

        prediction = response.json()

    return StrategyResponse(
        id="strategy_123",
        name=strategy.name,
        predicted_yield=prediction["pred"],
        status="active",
    )
