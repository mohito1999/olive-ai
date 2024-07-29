from typing import Optional

from constants import CampaignStatus, CampaignType

from .base import BaseSchema
from .customer_set import CustomerSetDBSchema


class CampaignDBInputSchema(BaseSchema):
    organization_id: str
    name: Optional[str]
    description: Optional[str]
    type: str
    status: str
    prompt: str
    initial_message: str
    max_duration: int
    max_retries: int
    end_date: Optional[str]
    telephony_service_id: Optional[str]
    telephony_service_config: Optional[dict]
    transcriber_id: Optional[str]
    transcriber_config: Optional[dict]
    agent_id: Optional[str]
    agent_config: Optional[dict]
    synthesizer_id: Optional[str]
    synthesizer_config: Optional[dict]
    created_by: str
    updated_by: str


class CampaignDBNoRelSchema(CampaignDBInputSchema):
    id: str


class CampaignDBSchema(CampaignDBNoRelSchema):
    customer_sets: list[CustomerSetDBSchema]


class CreateCampaignRequest(BaseSchema):
    organization_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    type: CampaignType
    status: Optional[CampaignStatus] = CampaignStatus.DRAFT
    prompt: str
    initial_message: str
    max_duration: int
    max_retries: int
    end_date: Optional[str] = None
    telephony_service_id: Optional[str] = None
    telephony_service_config: Optional[dict] = None
    transcriber_id: Optional[str] = None
    transcriber_config: Optional[dict] = None
    agent_id: Optional[str] = None
    agent_config: Optional[dict] = None
    synthesizer_id: Optional[str] = None
    synthesizer_config: Optional[dict] = None
    customer_sets: Optional[list[str]] = None


class CampaignResponse(CreateCampaignRequest):
    id: str
    customer_sets: list[CustomerSetDBSchema]


class UpdateCampaignRequest(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    prompt: Optional[str] = None
    initial_message: Optional[str] = None
    max_duration: Optional[int] = None
    max_retries: Optional[int] = None
    end_date: Optional[str] = None
    telephony_service_id: Optional[str] = None
    telephony_service_config: Optional[dict] = None
    transcriber_id: Optional[str] = None
    transcriber_config: Optional[dict] = None
    agent_id: Optional[str] = None
    agent_config: Optional[dict] = None
    synthesizer_id: Optional[str] = None
    synthesizer_config: Optional[dict] = None
    customer_sets: Optional[list[str]] = None


class TestCampaignRequest(BaseSchema):
    customer_id: str


class TestCampaignResponse(BaseSchema):
    call_id: str
    message: str
