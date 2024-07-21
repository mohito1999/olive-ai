# -*- coding: utf-8 -*-

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB

from constants import CampaignStatus, CampaignType

from .audit import AuditMixin
from .base import Base, BaseMeta


class Campaign(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "campaign"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('campaign')"),
    )
    organization_id = Column(String, ForeignKey("organization.id"), nullable=False)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False, default=CampaignType.OUTBOUND)
    status = Column(String, nullable=False, server_default=CampaignStatus.DRAFT.value)
    prompt = Column(String, nullable=False)
    max_duration = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=0)
    end_date = Column(DateTime, nullable=True)

    # Overrides
    telephony_service_id = Column(String, ForeignKey("telephony_service.id"), nullable=True)
    telephony_service_config = Column(JSONB, nullable=True)
    transcriber_id = Column(String, ForeignKey("transcriber.id"),nullable=True)
    transcriber_config = Column(JSONB, nullable=True)
    agent_id = Column(String, ForeignKey("agent.id"), nullable=True)
    agent_config = Column(JSONB, nullable=True)
    synthesizer_id = Column(String, ForeignKey("synthesizer.id"), nullable=True)
    synthesizer_config = Column(JSONB, nullable=True)

