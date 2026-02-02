from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import hashlib
from datetime import datetime, timedelta
import nacl.signing
import nacl.encoding
from eth_account.messages import encode_defunct
from eth_account import Account
import base58
import os

from .db import get_db_session
from .repositories import UserRepository

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


class WalletAuthRequest(BaseModel):
    address: str
    signature: str
    chain: str
    message: str


class AuthResponse(BaseModel):
    token: str
    user: dict
    expires_at: str


def verify_solana_signature(address: str, signature: str, message: str) -> bool:
    try:
        public_key_bytes = base58.b58decode(address)
        signature_bytes = base58.b58decode(signature)
        verify_key = nacl.signing.VerifyKey(public_key_bytes)
        verify_key.verify(message.encode('utf-8'), signature_bytes)
        return True
    except Exception:
        return False


def verify_ethereum_signature(address: str, signature: str, message: str) -> bool:
    try:
        message_encoded = encode_defunct(text=message)
        recovered_address = Account.recover_message(message_encoded, signature=signature)
        return recovered_address.lower() == address.lower()
    except Exception:
        return False


def create_jwt_token(user_id: int, wallet_address: str, chain: str) -> str:
    payload = {
        "user_id": user_id,
        "wallet_address": wallet_address,
        "chain": chain,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_db_session),
):
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

    repo = UserRepository(session)
    user = await repo.get_by_id(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/auth/wallet", response_model=AuthResponse)
async def authenticate_wallet(
    request: WalletAuthRequest,
    session: AsyncSession = Depends(get_db_session),
):
    if request.chain == "solana":
        is_valid = verify_solana_signature(request.address, request.signature, request.message)
    elif request.chain == "ethereum":
        is_valid = verify_ethereum_signature(request.address, request.signature, request.message)
    else:
        raise HTTPException(status_code=400, detail="Unsupported blockchain")

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    repo = UserRepository(session)
    user, created = await repo.get_or_create(request.address)

    token = create_jwt_token(user.id, request.address, request.chain)

    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "wallet_address": user.wallet_address,
            "chain": request.chain,
            "created_at": user.created_at.isoformat(),
        },
        expires_at=(datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)).isoformat(),
    )


@router.get("/auth/verify")
async def verify_auth(current_user=Depends(get_current_user)):
    return {"valid": True, "user": {"id": current_user.id, "wallet_address": current_user.wallet_address}}


@router.post("/auth/logout")
async def logout(current_user=Depends(get_current_user)):
    return {"message": "Logged out successfully"}


@router.get("/auth/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "wallet_address": current_user.wallet_address,
        "created_at": current_user.created_at.isoformat(),
        "is_active": current_user.is_active,
    }
