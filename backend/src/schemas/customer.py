from typing import Optional

from .base import BaseSchema


class CustomerDBInputSchema(BaseSchema):
    organization_id: str
    customer_set_id: Optional[str] = None
    name: str
    mobile_number: str
    customer_metadata: dict
    created_by: str
    updated_by: str


class CustomerDBSchema(CustomerDBInputSchema):
    id: str


class CreateCustomerRequest(BaseSchema):
    organization_id: str
    customer_set_id: Optional[str] = None
    name: str
    mobile_number: str
    customer_metadata: dict


class CustomerResponse(CreateCustomerRequest):
    id: str


class UpdateCustomerRequest(BaseSchema):
    name: Optional[str] = None
    mobile_number: Optional[str] = None
    customer_metadata: Optional[dict] = None

