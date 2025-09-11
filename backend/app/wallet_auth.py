from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import jwt
import hashlib
import time
from datetime import datetime, timedelta
import nacl.signing
import nacl.encoding
from eth_account.messages import encode_defunct
from eth_account import Account
import base58

router = APIRouter()

# JWT Secret - In production, use environment variable
JWT_SECRET = "your-secret-key-change-in-production"
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

class User(BaseModel):
    id: str
    wallet_address: str
    chain: str
    created_at: str
    last_login: str

# Mock user database - Replace with real database
users_db = {}

def verify_solana_signature(address: str, signature: str, message: str) -> bool:
    """Verify Solana wallet signature"""
    try:
        # Decode the public key from base58
        public_key_bytes = base58.b58decode(address)
        
        # Decode the signature from base58
        signature_bytes = base58.b58decode(signature)
        
        # Create a verifying key from the public key
        verify_key = nacl.signing.VerifyKey(public_key_bytes)
        
        # Verify the signature
        verify_key.verify(message.encode('utf-8'), signature_bytes)
        return True
    except Exception as e:
        print(f"Solana signature verification failed: {e}")
        return False

def verify_ethereum_signature(address: str, signature: str, message: str) -> bool:
    """Verify Ethereum wallet signature"""
    try:
        # Encode the message
        message_encoded = encode_defunct(text=message)
        
        # Recover the address from the signature
        recovered_address = Account.recover_message(message_encoded, signature=signature)
        
        # Compare addresses (case-insensitive)
        return recovered_address.lower() == address.lower()
    except Exception as e:
        print(f"Ethereum signature verification failed: {e}")
        return False

def create_jwt_token(user_id: str, wallet_address: str, chain: str) -> str:
    """Create a JWT token for authenticated user"""
    payload = {
        "user_id": user_id,
        "wallet_address": wallet_address,
        "chain": chain,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = verify_jwt_token(token)
        user_id = payload.get("user_id")
        
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return users_db[user_id]
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

@router.post("/auth/wallet", response_model=AuthResponse)
async def authenticate_wallet(request: WalletAuthRequest):
    """Authenticate user with wallet signature"""
    
    # Verify the signature based on chain
    is_valid = False
    
    if request.chain == "solana":
        is_valid = verify_solana_signature(
            request.address, 
            request.signature, 
            request.message
        )
    elif request.chain == "ethereum":
        is_valid = verify_ethereum_signature(
            request.address, 
            request.signature, 
            request.message
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported blockchain")
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Create or get user
    user_id = hashlib.sha256(f"{request.chain}:{request.address}".encode()).hexdigest()[:16]
    
    if user_id not in users_db:
        # Create new user
        users_db[user_id] = {
            "id": user_id,
            "wallet_address": request.address,
            "chain": request.chain,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
    else:
        # Update last login
        users_db[user_id]["last_login"] = datetime.utcnow().isoformat()
    
    # Create JWT token
    token = create_jwt_token(user_id, request.address, request.chain)
    
    return AuthResponse(
        token=token,
        user=users_db[user_id],
        expires_at=(datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)).isoformat()
    )

@router.get("/auth/verify")
async def verify_auth(current_user: dict = Depends(get_current_user)):
    """Verify if the current authentication token is valid"""
    return {
        "valid": True,
        "user": current_user
    }

@router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout the current user (client should remove the token)"""
    # In a real implementation, you might want to blacklist the token
    return {"message": "Logged out successfully"}

@router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
