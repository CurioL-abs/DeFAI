from fastapi import APIRouter, Depends, HTTPException
from .schemas import StrategyCreate, StrategyResponse
from .auth import get_current_user
import httpx

router = APIRouter()

@router.post("/strategies", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate, user=Depends(get_current_user)):
    # Call AI service for prediction
    async with httpx.AsyncClient() as client:
        response = await client.post("http://ai:8001/predict", 
                                   json={"strategy_id": strategy.name})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI service error")
        
        prediction = response.json()
    
    return StrategyResponse(
        id="strategy_123",
        name=strategy.name,
        predicted_yield=prediction["pred"],
        status="active"
    )
