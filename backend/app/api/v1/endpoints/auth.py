"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict
import uuid
import jwt
from passlib.context import CryptContext
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, CaptchaResponse, GithubTokenUpdate
from app.config import settings

router = APIRouter()

# Security configuration
# Explicitly set bcrypt to avoid passlib version detection issues with newer bcrypt versions
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# In-memory captcha store (for basic implementation)
captcha_store: Dict[str, int] = {}


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha():
    """Generate a basic math captcha"""
    import random
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    captcha_id = str(uuid.uuid4())
    answer = num1 + num2
    captcha_store[captcha_id] = answer
    
    # Cleanup old captchas (very basic cleanup)
    if len(captcha_store) > 100:
        # Remove first 50 keys
        keys = list(captcha_store.keys())[:50]
        for k in keys:
            captcha_store.pop(k, None)
            
    return CaptchaResponse(
        id=captcha_id,
        question=f"What is {num1} + {num2}?"
    )

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user with captcha verification"""
    # 1. Verify captcha
    stored_answer = captcha_store.pop(user_data.captcha_id, None)
    if stored_answer is None or stored_answer != user_data.captcha_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha"
        )
        
    # 2. Check if user exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # 3. Create user
    new_user = User(
        username=user_data.username,
        password_hash=pwd_context.hash(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        created_at=new_user.created_at,
        has_github_token=False
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with username/password and captcha verification"""
    # 1. Verify captcha
    stored_answer = captcha_store.pop(user_data.captcha_id, None)
    if stored_answer is None or stored_answer != user_data.captcha_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha"
        )
        
    # 2. Authenticate user
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Generate token
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        has_github_token=current_user.github_token is not None
    )


@router.post("/github-token", response_model=UserResponse)
async def update_github_token(
    token_data: GithubTokenUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's GitHub token"""
    current_user.github_token = token_data.github_token
    await db.commit()
    await db.refresh(current_user)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        has_github_token=True
    )


@router.delete("/github-token", response_model=UserResponse)
async def delete_github_token(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect user's GitHub account"""
    current_user.github_token = None
    await db.commit()
    await db.refresh(current_user)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        has_github_token=False
    )

# Made with Bob
