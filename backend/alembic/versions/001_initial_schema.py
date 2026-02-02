"""Initial schema - users, agents, strategies, transactions, performance

Revision ID: 001
Revises: None
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("wallet_address", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index("ix_users_wallet_address", "users", ["wallet_address"], unique=True)

    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="paused"),
        sa.Column("risk_tolerance", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("max_position_size", sa.Float(), nullable=False, server_default="1000.0"),
        sa.Column("wallet_address", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_agents_user_id", "agents", ["user_id"])

    op.create_table(
        "strategies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("strategy_type", sa.Text(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("config", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_strategies_agent_id", "strategies", ["agent_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("strategies.id"), nullable=True),
        sa.Column("tx_hash", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column("blockchain", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, server_default="solana"),
        sa.Column("transaction_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("token_in", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("token_out", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("profit_loss", sa.Float(), nullable=True),
        sa.Column("gas_fee", sa.Float(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, server_default="pending"),
        sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_transactions_agent_id", "transactions", ["agent_id"])
    op.create_index("ix_transactions_tx_hash", "transactions", ["tx_hash"])

    op.create_table(
        "performance",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("total_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("daily_pnl", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_pnl", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("win_rate", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("total_trades", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successful_trades", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sharpe_ratio", sa.Float(), nullable=True),
        sa.Column("max_drawdown", sa.Float(), nullable=True),
    )
    op.create_index("ix_performance_agent_id", "performance", ["agent_id"])
    op.create_index("ix_performance_date", "performance", ["date"])


def downgrade() -> None:
    op.drop_table("performance")
    op.drop_table("transactions")
    op.drop_table("strategies")
    op.drop_table("agents")
    op.drop_table("users")
