from typing import Optional

from pydantic import EmailStr, Field

from constants import UserRole

from .base import BaseSchema


class RegisterRequest(BaseSchema):
    name: Optional[str]
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    organization_id: str


class LoginRquest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)

