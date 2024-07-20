from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from constants import UserRole

from .base import BaseSchema


class RegisterRequest(BaseSchema):
    name: Optional[str]
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    organization_id: str


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class LoginResponse(BaseSchema):
    id: UUID
    name: str
    access_token: str
    expires_in: int
    refresh_token: str

