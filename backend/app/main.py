from fastapi import FastAPI
from .routes import router
from .db import init_db
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="DeFAI Forecast Optimizer - Backend")
app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status":"ok"}
