from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import SQLModel, Field, Relationship, JSON, Column, select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class AgentPerformance(SQLModel, table=True):
    """Daily/periodic performance snapshots for agents"""
    
    # Primary fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    agent_id: str = Field(foreign_key="agent.id", index=True)
    
    # Time period
    date: datetime = Field(index=True)  # Date this performance snapshot represents
    period_type: str = Field(default="daily", max_length=20)  # "hourly", "daily", "weekly", "monthly"
    
    # Performance metrics for the period
    trades_count: int = Field(default=0)
    successful_trades: int = Field(default=0)
    failed_trades: int = Field(default=0)
    
    # Financial metrics
    total_volume: float = Field(default=0.0)  # Total volume traded
    total_profit: float = Field(default=0.0)  # Total profit/loss
    total_fees: float = Field(default=0.0)    # Total fees paid
    net_profit: float = Field(default=0.0)    # Profit after fees
    
    # Performance ratios
    success_rate: float = Field(default=0.0)  # Percentage of successful trades
    profit_factor: float = Field(default=0.0)  # Total profit / Total loss
    average_profit: float = Field(default=0.0)  # Average profit per trade
    roi_percent: float = Field(default=0.0)    # Return on investment percentage
    
    # Risk metrics
    max_drawdown: float = Field(default=0.0)  # Maximum drawdown percentage
    volatility: float = Field(default=0.0)    # Volatility of returns
    sharpe_ratio: Optional[float] = Field(default=None)  # Risk-adjusted returns
    
    # Market context
    market_conditions: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Portfolio state at end of period
    portfolio_value: float = Field(default=0.0)
    positions: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Additional metrics
    avg_trade_duration: Optional[float] = Field(default=None)  # Average trade duration in seconds
    protocols_used: int = Field(default=0)  # Number of different protocols used
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    agent: "Agent" = Relationship(back_populates="performance_records")
    
    @classmethod
    async def get_by_agent_and_date(cls, session: AsyncSession, agent_id: str, date: datetime) -> Optional["AgentPerformance"]:
        """Get performance record for specific agent and date"""
        statement = select(cls).where(
            cls.agent_id == agent_id,
            cls.date == date.date()
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_agent_history(cls, session: AsyncSession, agent_id: str, days: int = 30) -> list["AgentPerformance"]:
        """Get performance history for an agent"""
        start_date = datetime.utcnow() - timedelta(days=days)
        statement = select(cls).where(
            cls.agent_id == agent_id,
            cls.date >= start_date.date()
        ).order_by(cls.date.desc())
        result = await session.execute(statement)
        return result.scalars().all()
    
    @classmethod
    async def get_top_performers(cls, session: AsyncSession, period_days: int = 7, limit: int = 10) -> list["AgentPerformance"]:
        """Get top performing agents in the specified period"""
        start_date = datetime.utcnow() - timedelta(days=period_days)
        statement = (
            select(cls)
            .where(cls.date >= start_date.date())
            .order_by(cls.roi_percent.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def save(self, session: AsyncSession):
        """Save performance record"""
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self
    
    def calculate_metrics(self):
        """Calculate derived performance metrics"""
        # Success rate
        if self.trades_count > 0:
            self.success_rate = (self.successful_trades / self.trades_count) * 100
            self.average_profit = self.total_profit / self.trades_count
        
        # Net profit after fees
        self.net_profit = self.total_profit - self.total_fees
        
        # ROI percentage
        if self.total_volume > 0:
            self.roi_percent = (self.net_profit / self.total_volume) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert performance record to dictionary"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "date": self.date.isoformat() if self.date else None,
            "period_type": self.period_type,
            "trades_count": self.trades_count,
            "successful_trades": self.successful_trades,
            "failed_trades": self.failed_trades,
            "total_volume": self.total_volume,
            "total_profit": self.total_profit,
            "total_fees": self.total_fees,
            "net_profit": self.net_profit,
            "success_rate": self.success_rate,
            "profit_factor": self.profit_factor,
            "average_profit": self.average_profit,
            "roi_percent": self.roi_percent,
            "max_drawdown": self.max_drawdown,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "portfolio_value": self.portfolio_value,
            "avg_trade_duration": self.avg_trade_duration,
            "protocols_used": self.protocols_used,
        }

class PortfolioSnapshot(SQLModel, table=True):
    """Point-in-time portfolio snapshots for agents"""
    
    # Primary fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    agent_id: str = Field(foreign_key="agent.id", index=True)
    
    # Snapshot details
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    snapshot_type: str = Field(default="periodic", max_length=20)  # "periodic", "pre_trade", "post_trade"
    
    # Portfolio composition
    positions: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Token positions
    protocols: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Protocol exposures
    
    # Value metrics
    total_value_usd: float = Field(default=0.0)
    sol_balance: float = Field(default=0.0)
    token_values: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    
    # Risk metrics
    concentration_risk: float = Field(default=0.0)  # Percentage in largest position
    protocol_diversification: float = Field(default=0.0)  # Number of protocols used
    
    # Market data at snapshot time
    market_prices: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    
    @classmethod
    async def get_latest_by_agent(cls, session: AsyncSession, agent_id: str) -> Optional["PortfolioSnapshot"]:
        """Get latest portfolio snapshot for an agent"""
        statement = select(cls).where(
            cls.agent_id == agent_id
        ).order_by(cls.timestamp.desc()).limit(1)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_agent_snapshots(cls, session: AsyncSession, agent_id: str, hours: int = 24) -> list["PortfolioSnapshot"]:
        """Get recent portfolio snapshots for an agent"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        statement = select(cls).where(
            cls.agent_id == agent_id,
            cls.timestamp >= start_time
        ).order_by(cls.timestamp.desc())
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def save(self, session: AsyncSession):
        """Save portfolio snapshot"""
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

# API Models
class AgentPerformanceResponse(SQLModel):
    """API response for agent performance"""
    id: str
    agent_id: str
    date: datetime
    period_type: str
    trades_count: int
    successful_trades: int
    total_profit: float
    net_profit: float
    success_rate: float
    roi_percent: float
    portfolio_value: float

class PerformanceSummary(SQLModel):
    """Summary performance statistics"""
    agent_id: str
    total_trades: int
    total_profit: float
    success_rate: float
    best_day_profit: float
    worst_day_profit: float
    avg_daily_return: float
    total_fees: float
    current_portfolio_value: float
    
class LeaderboardEntry(SQLModel):
    """Leaderboard entry for top performing agents"""
    agent_id: str
    agent_name: str
    owner_id: str
    period_return: float
    total_trades: int
    success_rate: float
    total_profit: float
    risk_score: float
    rank: int
