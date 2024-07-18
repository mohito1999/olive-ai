from typing import Optional

from .base import BaseSchema


class UserDBInputSchema(BaseSchema):
    name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str]
    auth_provider: str
    auth_provider_id: str
    role: str
    organization_id: str


class UserDBSchema(UserDBInputSchema):
    id: str


class CreateUserRequest(BaseSchema):
    name: Optional[str]
    email: Optional[str]
    mobile_number: Optional[str]
    auth_provider: str
    auth_provider_id: str
    role: str
    organization_id: str


class UserResponse(CreateUserRequest):
    id: str

