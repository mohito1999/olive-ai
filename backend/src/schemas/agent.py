from typing import Optional

from .base import BaseSchema


class AgentDBInputSchema(BaseSchema):
    name: str
    config: Optional[dict]
    created_by: str
    updated_by: str


class AgentDBSchema(AgentDBInputSchema):
    id: str


class CreateAgentRequest(BaseSchema):
    name: str
    config: Optional[dict]


class AgentResponse(CreateAgentRequest):
    id: str


class UpdateAgentRequest(BaseSchema):
    name: Optional[str] = None
    config: Optional[dict] = None
