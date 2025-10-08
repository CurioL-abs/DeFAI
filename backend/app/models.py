from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class StrategyType(str, Enum):
    YIELD_FARMING = "yield_farming"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    REBALANCING = "rebalancing"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_address: str = Field(unique=True, index=True, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

class Agent(SQLModel, table=True):
    __tablename__ = "agents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    status: AgentStatus = Field(default=AgentStatus.PAUSED)
    
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    max_position_size: float = Field(default=1000.0)
    
    wallet_address: Optional[str] = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
class Strategy(SQLModel, table=True):
    __tablename__ = "strategies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    strategy_type: StrategyType
    name: str = Field(max_length=100)
    
    config: str = Field(default="{}")
    is_active: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    strategy_id: Optional[int] = Field(foreign_key="strategies.id")
    
    tx_hash: Optional[str] = Field(max_length=200, index=True)
    blockchain: str = Field(default="solana", max_length=50)
    
    transaction_type: str = Field(max_length=50)
    amount: float
    token_in: Optional[str] = Field(max_length=50)
    token_out: Optional[str] = Field(max_length=50)
    
    profit_loss: Optional[float] = None
    gas_fee: Optional[float] = None
    
    status: str = Field(default="pending", max_length=50)
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class Performance(SQLModel, table=True):
    __tablename__ = "performance"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    
    date: datetime = Field(default_factory=datetime.utcnow, index=True)
    total_value: float = Field(default=0.0)
    daily_pnl: float = Field(default=0.0)
    total_pnl: float = Field(default=0.0)
    
    win_rate: Optional[float] = Field(default=0.0)
    total_trades: int = Field(default=0)
    successful_trades: int = Field(default=0)
    
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None

