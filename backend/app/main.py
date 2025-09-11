from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .wallet_auth import router as auth_router
from .db import init_db
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="DeFAI Forecast Optimizer - Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(auth_router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status":"ok"}
