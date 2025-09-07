from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, JSON, Column, select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class AgentStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active" 
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Agent(SQLModel, table=True):
    """AI Agent model for autonomous DeFi strategies"""
    
    # Primary fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Agent configuration
    strategy_type: str = Field(max_length=50)  # "yield_farming", "arbitrage", "lending", etc.
    strategy_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    
    # Wallet and blockchain info
    wallet_address: Optional[str] = Field(default=None, max_length=100)
    chain: str = Field(default="solana", max_length=20)
    
    # Protocols and tokens to interact with
    protocols: List[str] = Field(default=[], sa_column=Column(JSON))
    watched_tokens: List[str] = Field(default=[], sa_column=Column(JSON))
    
    # Financial constraints
    max_investment: float = Field(default=1000.0, gt=0)  # Maximum amount to invest
    min_profit_threshold: float = Field(default=0.01)    # Minimum 1% profit to execute
    stop_loss_percent: float = Field(default=0.1)        # 10% stop loss
    
    # Status and lifecycle
    status: AgentStatus = Field(default=AgentStatus.CREATED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = Field(default=None)
    
    # User and permissions
    owner_id: str = Field(max_length=100)  # User who owns this agent
    is_public: bool = Field(default=False)  # Can other users copy this agent?
    
    # Performance tracking
    total_profit: float = Field(default=0.0)
    total_trades: int = Field(default=0)
    success_rate: float = Field(default=0.0)  # Percentage of successful trades
    
    # Relationships
    executions: List["StrategyExecution"] = Relationship(back_populates="agent")
    performance_records: List["AgentPerformance"] = Relationship(back_populates="agent")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    @classmethod
    async def get(cls, session: AsyncSession, agent_id: str) -> Optional["Agent"]:
        """Get agent by ID"""
        statement = select(cls).where(cls.id == agent_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_owner(cls, session: AsyncSession, owner_id: str) -> List["Agent"]:
        """Get all agents for a specific owner"""
        statement = select(cls).where(cls.owner_id == owner_id)
        result = await session.execute(statement)
        return result.scalars().all()
    
    @classmethod
    async def get_active_agents(cls, session: AsyncSession) -> List["Agent"]:
        """Get all active agents"""
        statement = select(cls).where(cls.status == AgentStatus.ACTIVE)
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def save(self, session: AsyncSession):
        """Save agent to database"""
        self.updated_at = datetime.utcnow()
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self
    
    async def update_status(self, session: AsyncSession, new_status: AgentStatus):
        """Update agent status"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        if new_status == AgentStatus.ACTIVE:
            self.last_active_at = datetime.utcnow()
        await self.save(session)
    
    async def update_performance(self, session: AsyncSession, profit: float, success: bool):
        """Update agent performance metrics"""
        self.total_profit += profit
        self.total_trades += 1
        
        # Calculate success rate
        if self.total_trades > 0:
            # This is simplified - in production, track successful trades separately
            current_successes = int(self.success_rate * (self.total_trades - 1) / 100)
            if success:
                current_successes += 1
            self.success_rate = (current_successes / self.total_trades) * 100
        
        await self.save(session)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "strategy_type": self.strategy_type,
            "strategy_config": self.strategy_config,
            "risk_level": self.risk_level,
            "wallet_address": self.wallet_address,
            "chain": self.chain,
            "protocols": self.protocols,
            "watched_tokens": self.watched_tokens,
            "max_investment": self.max_investment,
            "min_profit_threshold": self.min_profit_threshold,
            "stop_loss_percent": self.stop_loss_percent,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "owner_id": self.owner_id,
            "is_public": self.is_public,
            "total_profit": self.total_profit,
            "total_trades": self.total_trades,
            "success_rate": self.success_rate,
        }

# Pydantic models for API
class AgentCreate(SQLModel):
    """Model for creating a new agent"""
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    strategy_type: str = Field(max_length=50)
    strategy_config: Dict[str, Any] = Field(default={})
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    protocols: List[str] = Field(default=[])
    watched_tokens: List[str] = Field(default=[])
    max_investment: float = Field(default=1000.0, gt=0)
    min_profit_threshold: float = Field(default=0.01, gt=0, le=1)
    stop_loss_percent: float = Field(default=0.1, gt=0, le=1)
    is_public: bool = Field(default=False)

class AgentUpdate(SQLModel):
    """Model for updating an agent"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    strategy_config: Optional[Dict[str, Any]] = Field(default=None)
    risk_level: Optional[RiskLevel] = Field(default=None)
    protocols: Optional[List[str]] = Field(default=None)
    watched_tokens: Optional[List[str]] = Field(default=None)
    max_investment: Optional[float] = Field(default=None, gt=0)
    min_profit_threshold: Optional[float] = Field(default=None, gt=0, le=1)
    stop_loss_percent: Optional[float] = Field(default=None, gt=0, le=1)
    is_public: Optional[bool] = Field(default=None)

class AgentResponse(SQLModel):
    """Model for agent API responses"""
    id: str
    name: str
    description: Optional[str] = None
    strategy_type: str
    strategy_config: Dict[str, Any] = {}
    risk_level: RiskLevel
    wallet_address: Optional[str] = None
    chain: str
    protocols: List[str] = []
    watched_tokens: List[str] = []
    max_investment: float
    min_profit_threshold: float
    stop_loss_percent: float
    status: AgentStatus
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None
    owner_id: str
    is_public: bool
    total_profit: float
    total_trades: int
    success_rate: float
