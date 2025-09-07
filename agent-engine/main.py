from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv

from core.agent_manager import AgentManager
from core.strategy_engine import StrategyEngine
from core.solana_client import SolanaClientManager
from api import agents, strategies, monitoring
from models import database

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    # Initialize database
    await database.init_db()
    
    # Initialize Solana connection
    solana_manager = SolanaClientManager()
    await solana_manager.initialize()
    
    # Initialize core services
    app.state.agent_manager = AgentManager()
    app.state.strategy_engine = StrategyEngine()
    
    # Start background tasks
    asyncio.create_task(app.state.agent_manager.run_agent_loop())
    
    yield
    
    # Cleanup
    await solana_manager.close()

app = FastAPI(
    title="DeFAI Agent Engine",
    description="Autonomous AI agents for Solana DeFi",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agent-engine",
        "solana_connected": True  # TODO: Add actual health check
    }

@app.get("/")
async def root():
    return {
        "message": "DeFAI Agent Engine",
        "docs": "/docs",
        "agents": "/agents",
        "strategies": "/strategies"
    }
