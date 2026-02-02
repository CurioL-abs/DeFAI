from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .wallet_auth import router as auth_router
from .db import init_db, test_db_connection
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(title="DeFAI Forecast Optimizer - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup():
    logger.info("Starting DeFAI Backend...")
    try:
        await init_db()
        logger.info("Backend startup complete")
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        raise


@app.get("/health")
async def health():
    return {"status": "ok", "service": "backend"}


@app.get("/health/db")
async def health_db():
    db_ok = await test_db_connection()
    return {
        "status": "ok" if db_ok else "error",
        "database": "connected" if db_ok else "disconnected",
    }
