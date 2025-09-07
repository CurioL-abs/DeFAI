from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    admin_key = os.getenv("ADMIN_API_KEY", "admin_demo_key_please_change")
    if credentials.credentials != admin_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"user_id": "admin"}
