from typing import Optional

from constants import CustomerSetStatus, CustomerSetType

from .base import BaseSchema


class CustomerSetDBInputSchema(BaseSchema):
    organization_id: str
    name: Optional[str]
    description: Optional[str]
    type: CustomerSetType
    status: CustomerSetStatus
    url: Optional[str] = None
    created_by: str
    updated_by: str


class CustomerSetDBSchema(CustomerSetDBInputSchema):
    id: str


class CreateCustomerSetRequest(BaseSchema):
    organization_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    type: CustomerSetType
    url: Optional[str] = None


class CustomerSetResponse(CreateCustomerSetRequest):
    id: str


class UpdateCustomerSetRequest(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None

