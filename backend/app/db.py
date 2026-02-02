import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/defai_agents"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db_session() -> AsyncSession:
    """FastAPI dependency that yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def init_db():
    """Create tables and stamp Alembic version for future migrations."""
    try:
        from .models import User, Agent, Strategy, Transaction, Performance  # noqa: F401
        from alembic.config import Config
        from alembic import command
        import os

        # Create all tables using SQLModel metadata (handles enums correctly)
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        # Stamp with current Alembic revision so future migrations work
        alembic_dir = os.path.join(os.path.dirname(__file__), "..", "alembic")
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        alembic_cfg.set_main_option("script_location", alembic_dir)

        async with engine.connect() as conn:
            await conn.run_sync(_stamp_alembic, alembic_cfg)
            await conn.commit()

        logger.info("Database initialized and Alembic version stamped")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def _stamp_alembic(connection, alembic_cfg):
    from alembic import command
    alembic_cfg.attributes["connection"] = connection
    command.stamp(alembic_cfg, "head")

async def test_db_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
