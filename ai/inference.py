from fastapi import FastAPI
from pydantic import BaseModel
from models.forecast_model import load_model
import numpy as np, os

app = FastAPI(title="DeFAI AI Service")
model = None

class PredictReq(BaseModel):
    strategy_id: str

@app.on_event("startup")
def load():
    global model
    if not os.path.exists("models/lightgbm_model.joblib"):
        import train; train.train()
    model = load_model()

@app.post("/predict")
def predict(req: PredictReq):
    hv = abs(hash(req.strategy_id)) % 1000 / 1000.0
    X = np.random.RandomState(int(hv*1000)).randn(1,10)
    pred = float(model.predict(X)[0])
    return {"strategy_id": req.strategy_id, "pred": pred}
