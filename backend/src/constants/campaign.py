from enum import Enum


class CampaignType(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class CampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
