from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import Optional, List
from datetime import datetime

from .models import User, Agent, AgentStatus, Strategy, StrategyType, Transaction, Performance


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, wallet_address: str) -> User:
        user = User(wallet_address=wallet_address)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_wallet(self, wallet_address: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.wallet_address == wallet_address)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, wallet_address: str) -> tuple[User, bool]:
        user = await self.get_by_wallet(wallet_address)
        if user:
            user.updated_at = datetime.utcnow()
            return user, False
        user = await self.create(wallet_address)
        return user, True

    async def deactivate(self, user_id: int) -> bool:
        result = await self.session.execute(
            update(User).where(User.id == user_id).values(is_active=False)
        )
        return result.rowcount > 0


class AgentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        risk_tolerance: float = 0.5,
        max_position_size: float = 1000.0,
    ) -> Agent:
        agent = Agent(
            user_id=user_id,
            name=name,
            description=description,
            risk_tolerance=risk_tolerance,
            max_position_size=max_position_size,
        )
        self.session.add(agent)
        await self.session.flush()
        return agent

    async def get_by_id(self, agent_id: int) -> Optional[Agent]:
        result = await self.session.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> List[Agent]:
        result = await self.session.execute(
            select(Agent).where(Agent.user_id == user_id).order_by(Agent.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active(self) -> List[Agent]:
        result = await self.session.execute(
            select(Agent).where(Agent.status == AgentStatus.ACTIVE)
        )
        return list(result.scalars().all())

    async def update_status(self, agent_id: int, status: AgentStatus) -> bool:
        result = await self.session.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        return result.rowcount > 0

    async def update(self, agent_id: int, **kwargs) -> Optional[Agent]:
        kwargs["updated_at"] = datetime.utcnow()
        await self.session.execute(
            update(Agent).where(Agent.id == agent_id).values(**kwargs)
        )
        return await self.get_by_id(agent_id)

    async def delete(self, agent_id: int) -> bool:
        result = await self.session.execute(
            delete(Agent).where(Agent.id == agent_id)
        )
        return result.rowcount > 0


class StrategyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        agent_id: int,
        strategy_type: StrategyType,
        name: str,
        config: str = "{}",
    ) -> Strategy:
        strategy = Strategy(
            agent_id=agent_id,
            strategy_type=strategy_type,
            name=name,
            config=config,
        )
        self.session.add(strategy)
        await self.session.flush()
        return strategy

    async def get_by_id(self, strategy_id: int) -> Optional[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        return result.scalar_one_or_none()

    async def get_by_agent(self, agent_id: int) -> List[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.agent_id == agent_id)
        )
        return list(result.scalars().all())

    async def get_active_by_agent(self, agent_id: int) -> List[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(
                Strategy.agent_id == agent_id, Strategy.is_active == True
            )
        )
        return list(result.scalars().all())

    async def deactivate(self, strategy_id: int) -> bool:
        result = await self.session.execute(
            update(Strategy).where(Strategy.id == strategy_id).values(is_active=False)
        )
        return result.rowcount > 0


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        agent_id: int,
        transaction_type: str,
        amount: float,
        strategy_id: Optional[int] = None,
        tx_hash: Optional[str] = None,
        token_in: Optional[str] = None,
        token_out: Optional[str] = None,
    ) -> Transaction:
        tx = Transaction(
            agent_id=agent_id,
            strategy_id=strategy_id,
            transaction_type=transaction_type,
            amount=amount,
            tx_hash=tx_hash,
            token_in=token_in,
            token_out=token_out,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def get_by_id(self, tx_id: int) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == tx_id)
        )
        return result.scalar_one_or_none()

    async def get_by_agent(
        self, agent_id: int, limit: int = 50, offset: int = 0
    ) -> List[Transaction]:
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.agent_id == agent_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.tx_hash == tx_hash)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        tx_id: int,
        status: str,
        profit_loss: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        values = {"status": status}
        if status in ("completed", "failed"):
            values["completed_at"] = datetime.utcnow()
        if profit_loss is not None:
            values["profit_loss"] = profit_loss
        if error_message is not None:
            values["error_message"] = error_message
        result = await self.session.execute(
            update(Transaction).where(Transaction.id == tx_id).values(**values)
        )
        return result.rowcount > 0


class PerformanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, agent_id: int, **kwargs) -> Performance:
        perf = Performance(agent_id=agent_id, **kwargs)
        self.session.add(perf)
        await self.session.flush()
        return perf

    async def get_by_agent(
        self, agent_id: int, limit: int = 30
    ) -> List[Performance]:
        result = await self.session.execute(
            select(Performance)
            .where(Performance.agent_id == agent_id)
            .order_by(Performance.date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest(self, agent_id: int) -> Optional[Performance]:
        result = await self.session.execute(
            select(Performance)
            .where(Performance.agent_id == agent_id)
            .order_by(Performance.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_summary(self, agent_id: int) -> dict:
        result = await self.session.execute(
            select(
                func.sum(Performance.daily_pnl).label("total_pnl"),
                func.avg(Performance.win_rate).label("avg_win_rate"),
                func.sum(Performance.total_trades).label("total_trades"),
                func.max(Performance.total_value).label("peak_value"),
            ).where(Performance.agent_id == agent_id)
        )
        row = result.one_or_none()
        if not row:
            return {"total_pnl": 0, "avg_win_rate": 0, "total_trades": 0, "peak_value": 0}
        return {
            "total_pnl": float(row.total_pnl or 0),
            "avg_win_rate": float(row.avg_win_rate or 0),
            "total_trades": int(row.total_trades or 0),
            "peak_value": float(row.peak_value or 0),
        }
