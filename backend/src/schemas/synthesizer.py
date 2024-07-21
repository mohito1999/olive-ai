from typing import Optional

from .base import BaseSchema


class SynthesizerDBInputSchema(BaseSchema):
    name: str
    config: Optional[dict]
    created_by: str
    updated_by: str


class SynthesizerDBSchema(SynthesizerDBInputSchema):
    id: str


class CreateSynthesizerRequest(BaseSchema):
    name: str
    config: Optional[dict]


class SynthesizerResponse(CreateSynthesizerRequest):
    id: str


class UpdateSynthesizerRequest(BaseSchema):
    name: Optional[str] = None
    config: Optional[dict] = None
