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

    class Config:
        from_attributes = True


class GithubTokenUpdate(BaseModel):
    github_token: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CaptchaResponse(BaseModel):
    id: str
    question: str

# Made with Bob
