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

