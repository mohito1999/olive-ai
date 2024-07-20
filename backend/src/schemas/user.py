from typing import Optional
from uuid import UUID

from .base import BaseSchema


class UserDBInputSchema(BaseSchema):
    name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str]
    auth_provider: str
    role: str
    organization_id: str


class UserDBSchema(UserDBInputSchema):
    id: UUID


class CreateUserRequest(BaseSchema):
    name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str]
    role: str
    organization_id: str


class UserResponse(CreateUserRequest):
    id: UUID

