from typing import Optional

from .base import BaseSchema


class TelephonyServiceDBInputSchema(BaseSchema):
    name: str
    config: Optional[dict]
    created_by: str
    updated_by: str


class TelephonyServiceDBSchema(TelephonyServiceDBInputSchema):
    id: str


class CreateTelephonyServiceRequest(BaseSchema):
    name: str
    config: Optional[dict]


class TelephonyServiceResponse(CreateTelephonyServiceRequest):
    id: str


class UpdateTelephonyServiceRequest(BaseSchema):
    name: Optional[str] = None
    config: Optional[dict] = None
