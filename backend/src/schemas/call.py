from typing import Optional

from vocode.streaming.models.agent import InterruptSensitivity

from constants import DEFAULT_INITIAL_MESSAGE, DEFAULT_PROMPT, DEFAULT_VOICE

from .base import BaseSchema


class CallDBInputSchema(BaseSchema):
    organization_id: str
    campaign_id: str
    customer_id: str
    type: str
    from_number: str
    to_number: str
    status: str
    retry_count: int
    duration: int
    recording_url: Optional[str]
    transcript: Optional[str]
    summary: Optional[str]
    telephony_service_id: str
    telephony_service_config: dict
    transcriber_id: str
    transcriber_config: dict
    agent_id: str
    agent_config: dict
    synthesizer_id: str
    synthesizer_config: dict


class CallDBSchema(CallDBInputSchema):
    id: str


class CreateCallRequest(BaseSchema):
    organization_id: str
    campaign_id: str
    customer_id: str
    type: str
    from_number: str
    to_number: str
    status: str
    retry_count: int
    duration: int
    recording_url: Optional[str]
    transcript: Optional[str]
    summary: Optional[str]
    telephony_service_id: str
    telephony_service_config: dict
    transcriber_id: str
    transcriber_config: dict
    agent_id: str
    agent_config: dict
    synthesizer_id: str
    synthesizer_config: dict


class CallResponse(CreateCallRequest):
    id: str


class OutboundCallRequest(BaseSchema):
    mobile_number: str
    name: str
    company: str
    company_product: str
    prompt: Optional[str] = DEFAULT_PROMPT
    initial_message: Optional[str] = DEFAULT_INITIAL_MESSAGE
    interrupt_sensitivity: Optional[InterruptSensitivity] = "low"
    voice: Optional[str] = DEFAULT_VOICE

