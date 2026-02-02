from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Strategy schemas
class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None


class StrategyResponse(BaseModel):
    id: str
    name: str
    predicted_yield: float
    status: str


# Agent schemas
class AgentCreate(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = None
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    max_position_size: float = Field(default=1000.0, gt=0)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    risk_tolerance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_position_size: Optional[float] = Field(default=None, gt=0)


class AgentResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    status: str
    risk_tolerance: float
    max_position_size: float
    wallet_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionResponse(BaseModel):
    id: int
    agent_id: int
    strategy_id: Optional[int]
    tx_hash: Optional[str]
    blockchain: str
    transaction_type: str
    amount: float
    token_in: Optional[str]
    token_out: Optional[str]
    profit_loss: Optional[float]
    gas_fee: Optional[float]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Performance schemas
class PerformanceResponse(BaseModel):
    id: int
    agent_id: int
    date: datetime
    total_value: float
    daily_pnl: float
    total_pnl: float
    win_rate: Optional[float]
    total_trades: int
    successful_trades: int
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]

    class Config:
        from_attributes = True


class PerformanceSummary(BaseModel):
    total_pnl: float
    avg_win_rate: float
    total_trades: int
    peak_value: float
