from pydantic import BaseModel
from typing import Optional

class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None

class StrategyResponse(BaseModel):
    id: str
    name: str
    predicted_yield: float
    status: str
