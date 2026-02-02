import os
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from models.forecast_model import load_model
from typing import Optional
import numpy as np

app = FastAPI(title="DeFAI AI Service")
model = None

INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "internal-key-change-in-production")


class PredictReq(BaseModel):
    strategy_id: str


def verify_internal_key(x_internal_key: Optional[str] = Header(None)):
    if not x_internal_key or x_internal_key != INTERNAL_SERVICE_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal service key")
    return True


@app.on_event("startup")
def load():
    global model
    if not os.path.exists("models/lightgbm_model.joblib"):
        import train; train.train()
    model = load_model()


@app.post("/predict")
def predict(req: PredictReq, _: bool = Depends(verify_internal_key)):
    hv = abs(hash(req.strategy_id)) % 1000 / 1000.0
    X = np.random.RandomState(int(hv*1000)).randn(1,10)
    pred = float(model.predict(X)[0])
    return {"strategy_id": req.strategy_id, "pred": pred}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai"}
