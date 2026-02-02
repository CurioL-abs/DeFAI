import os
import jwt
from fastapi import HTTPException, Header, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models import get_db_session

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "internal-key-change-in-production")


def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    authorization: Optional[str] = Header(None),
):
    """Extract user identity from JWT token. Returns the user_id as a string
    (used as owner_id in agent-engine's Agent model)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return str(user_id)


def verify_internal_key(x_internal_key: Optional[str] = Header(None)):
    """Verify service-to-service internal key."""
    if not x_internal_key or x_internal_key != INTERNAL_SERVICE_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal service key")
    return True
