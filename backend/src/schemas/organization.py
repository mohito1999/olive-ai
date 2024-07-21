from typing import Optional

from .base import BaseSchema


class OrganizationDBInputSchema(BaseSchema):
    name: str
    telephony_service_id: str
    telephony_service_config: dict
    transcriber_id: str
    transcriber_config: dict
    agent_id: str
    agent_config: dict
    synthesizer_id: str
    synthesizer_config: dict
    credits: int
    created_by: str
    updated_by: str


class OrganizationDBSchema(OrganizationDBInputSchema):
    id: str


class CreateOrganizationRequest(BaseSchema):
    name: str
    telephony_service_id: str
    telephony_service_config: dict
    transcriber_id: str
    transcriber_config: dict
    agent_id: str
    agent_config: dict
    synthesizer_id: str
    synthesizer_config: dict
    credits: int


class OrganizationResponse(CreateOrganizationRequest):
    id: str


class UpdateOrganizationRequest(BaseSchema):
    name: Optional[str] = None
    telephony_service_id: Optional[str] = None
    telephony_service_config: Optional[dict] = None
    transcriber_id: Optional[str] = None
    transcriber_config: Optional[dict] = None
    agent_id: Optional[str] = None
    agent_config: Optional[dict] = None
    synthesizer_id: Optional[str] = None
    synthesizer_config: Optional[dict] = None
    credits: Optional[int] = None

