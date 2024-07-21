from typing import Optional

from .base import BaseSchema


class TranscriberDBInputSchema(BaseSchema):
    name: str
    config: Optional[dict]
    created_by: str
    updated_by: str


class TranscriberDBSchema(TranscriberDBInputSchema):
    id: str


class CreateTranscriberRequest(BaseSchema):
    name: str
    config: Optional[dict]


class TranscriberResponse(CreateTranscriberRequest):
    id: str


class UpdateTranscriberRequest(BaseSchema):
    name: Optional[str] = None
    config: Optional[dict] = None
