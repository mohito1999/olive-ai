from typing import Optional

from .base import BaseSchema


class CampaignDBInputSchema(BaseSchema):
    organization_id: str
    type: str
    name: Optional[str]
    description: Optional[str]
    prompt: str
    max_duration: int
    max_retries: int
    end_date: Optional[str]
    language: str
    telephony_service_id: Optional[str]
    telephony_service_config: Optional[dict]
    transcriber_id: Optional[str]
    transcriber_config: Optional[dict]
    agent_id: Optional[str]
    agent_config: Optional[dict]
    synthesizer_id: Optional[str]
    synthesizer_config: Optional[dict]


class CampaignDBSchema(CampaignDBInputSchema):
    id: str


class CreateCampaignRequest(BaseSchema):
    organization_id: str
    type: str
    name: Optional[str]
    description: Optional[str]
    prompt: str
    max_duration: int
    max_retries: int
    end_date: Optional[str]
    language: str
    telephony_service_id: Optional[str]
    telephony_service_config: Optional[dict]
    transcriber_id: Optional[str]
    transcriber_config: Optional[dict]
    agent_id: Optional[str]
    agent_config: Optional[dict]
    synthesizer_id: Optional[str]
    synthesizer_config: Optional[dict]


class CampaignResponse(CreateCampaignRequest):
    id: str

