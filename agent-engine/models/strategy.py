from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, JSON, Column, select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class StrategyType(str, Enum):
    SWAP = "swap"
    LENDING = "lending"
    LIQUIDITY_PROVISION = "liquidity_provision"
    YIELD_FARMING = "yield_farming"
    ARBITRAGE = "arbitrage"
    MULTI_HOP = "multi_hop"

class Protocol(str, Enum):
    JUPITER = "jupiter"
    MARGINFI = "marginfi"
    ORCA = "orca"
    RAYDIUM = "raydium"
    KAMINO = "kamino"
    SOLEND = "solend"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StrategyExecution(SQLModel, table=True):
    """Record of strategy execution by an AI agent"""
    
    # Primary fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    agent_id: str = Field(foreign_key="agent.id", index=True)
    
    # Strategy details
    strategy_type: StrategyType
    protocol: Optional[Protocol] = Field(default=None)
    decision: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # ML decision that triggered this
    
    # Execution details
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[float] = Field(default=None)
    
    # Transaction details
    transaction_ids: List[str] = Field(default=[], sa_column=Column(JSON))  # Blockchain transaction IDs
    gas_fees: float = Field(default=0.0)
    
    # Financial results
    input_amount: float = Field(default=0.0)
    output_amount: float = Field(default=0.0)
    profit: float = Field(default=0.0)  # Actual profit/loss
    profit_percent: float = Field(default=0.0)  # Percentage profit
    expected_profit: float = Field(default=0.0)  # ML predicted profit
    
    # Market conditions at execution
    market_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Success and error tracking
    success: bool = Field(default=False)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    
    # Additional metadata
    execution_context: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Any additional context
    
    # Relationships
    agent: "Agent" = Relationship(back_populates="executions")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    @classmethod
    async def get(cls, session: AsyncSession, execution_id: str) -> Optional["StrategyExecution"]:
        """Get execution by ID"""
        statement = select(cls).where(cls.id == execution_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_agent(cls, session: AsyncSession, agent_id: str, limit: int = 100) -> List["StrategyExecution"]:
        """Get executions for a specific agent"""
        statement = select(cls).where(cls.agent_id == agent_id).order_by(cls.start_time.desc()).limit(limit)
        result = await session.execute(statement)
        return result.scalars().all()
    
    @classmethod
    async def get_recent(cls, session: AsyncSession, hours: int = 24, limit: int = 100) -> List["StrategyExecution"]:
        """Get recent executions within specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        statement = (
            select(cls)
            .where(cls.start_time >= cutoff_time)
            .order_by(cls.start_time.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return result.scalars().all()
    
    @classmethod
    async def get_successful_by_agent(cls, session: AsyncSession, agent_id: str) -> List["StrategyExecution"]:
        """Get successful executions for an agent"""
        statement = select(cls).where(
            cls.agent_id == agent_id,
            cls.success == True,
            cls.status == ExecutionStatus.COMPLETED
        ).order_by(cls.start_time.desc())
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def save(self, session: AsyncSession):
        """Save execution to database"""
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self
    
    async def complete_execution(self, session: AsyncSession, success: bool, profit: float = 0.0, error: str = None):
        """Mark execution as completed"""
        self.end_time = datetime.utcnow()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.profit = profit
        self.status = ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
        if error:
            self.error_message = error[:1000]  # Truncate long error messages
        
        await self.save(session)
    
    def calculate_profit_percent(self):
        """Calculate profit percentage"""
        if self.input_amount > 0:
            self.profit_percent = (self.profit / self.input_amount) * 100
        else:
            self.profit_percent = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "strategy_type": self.strategy_type,
            "protocol": self.protocol,
            "decision": self.decision,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "transaction_ids": self.transaction_ids,
            "gas_fees": self.gas_fees,
            "input_amount": self.input_amount,
            "output_amount": self.output_amount,
            "profit": self.profit,
            "profit_percent": self.profit_percent,
            "expected_profit": self.expected_profit,
            "success": self.success,
            "error_message": self.error_message,
        }

class Strategy(SQLModel, table=True):
    """Reusable strategy templates"""
    
    # Primary fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Strategy configuration
    strategy_type: StrategyType
    protocols: List[str] = Field(default=[], sa_column=Column(JSON))
    config_template: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Strategy metadata
    risk_level: str = Field(max_length=20)  # "low", "medium", "high"
    min_investment: float = Field(default=100.0)
    max_investment: float = Field(default=10000.0)
    expected_apy: Optional[float] = Field(default=None)  # Expected annual percentage yield
    
    # Strategy rules and constraints
    rules: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    constraints: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(max_length=100)  # User who created this strategy
    
    # Performance tracking
    total_uses: int = Field(default=0)
    average_profit: float = Field(default=0.0)
    success_rate: float = Field(default=0.0)
    
    # Visibility
    is_public: bool = Field(default=False)  # Can other users use this strategy?
    is_verified: bool = Field(default=False)  # Verified by platform
    
    @classmethod
    async def get(cls, session: AsyncSession, strategy_id: str) -> Optional["Strategy"]:
        """Get strategy by ID"""
        statement = select(cls).where(cls.id == strategy_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_public_strategies(cls, session: AsyncSession) -> List["Strategy"]:
        """Get all public strategies"""
        statement = select(cls).where(cls.is_public == True).order_by(cls.success_rate.desc())
        result = await session.execute(statement)
        return result.scalars().all()
    
    @classmethod
    async def get_by_type(cls, session: AsyncSession, strategy_type: StrategyType) -> List["Strategy"]:
        """Get strategies by type"""
        statement = select(cls).where(cls.strategy_type == strategy_type)
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def save(self, session: AsyncSession):
        """Save strategy to database"""
        self.updated_at = datetime.utcnow()
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

# API Models
class StrategyExecutionResponse(SQLModel):
    """API response model for strategy execution"""
    id: str
    agent_id: str
    strategy_type: StrategyType
    protocol: Optional[Protocol] = None
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    transaction_ids: List[str] = []
    profit: float
    profit_percent: float
    success: bool
    error_message: Optional[str] = None

class StrategyCreate(SQLModel):
    """Model for creating a new strategy"""
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    strategy_type: StrategyType
    protocols: List[str] = Field(default=[])
    config_template: Dict[str, Any] = Field(default={})
    risk_level: str = Field(max_length=20)
    min_investment: float = Field(default=100.0, gt=0)
    max_investment: float = Field(default=10000.0, gt=0)
    expected_apy: Optional[float] = Field(default=None, ge=0, le=10)  # 0-1000% APY
    rules: Dict[str, Any] = Field(default={})
    constraints: Dict[str, Any] = Field(default={})
    is_public: bool = Field(default=False)

from datetime import timedelta
