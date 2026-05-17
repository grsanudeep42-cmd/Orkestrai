"""
User Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    captcha_answer: int
    captcha_id: str


class UserLogin(UserBase):
    password: str
    captcha_answer: int
    captcha_id: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    has_github_token: bool = False
    has_openai_key: bool = False
    has_gemini_key: bool = False
    has_groq_key: bool = False
    has_openrouter_key: bool = False
    has_bob_key: bool = False

    class Config:
        from_attributes = True


class UserKeysUpdate(BaseModel):
    github_token: Optional[str] = None
    openai_key: Optional[str] = None
    gemini_key: Optional[str] = None
    groq_key: Optional[str] = None
    openrouter_key: Optional[str] = None
    bob_key: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CaptchaResponse(BaseModel):
    id: str
    question: str

# Made with Bob
