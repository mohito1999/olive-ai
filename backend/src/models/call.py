# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB

from constants import CallStatus

from .audit import AuditMixin
from .base import Base, BaseMeta


class Call(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "call"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('call')"),
    )
    organization_id = Column(String, ForeignKey("organization.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaign.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customer.id"), nullable=False)
    type = Column(String, nullable=False)
    from_number = Column(String, nullable=False)
    to_number = Column(String, nullable=False)
    status = Column(String, nullable=False, default=CallStatus.PENDING)
    retry_count = Column(Integer, nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=0)
    recording_url = Column(String, nullable=True)
    transcript = Column(String, nullable=True)
    summary = Column(String, nullable=True)

    telephony_service_id = Column(String, ForeignKey("telephony_service.id"), nullable=False)
    telephony_service_config = Column(JSONB, nullable=False)
    transcriber_id = Column(String, ForeignKey("transcriber.id"),nullable=False)
    transcriber_config = Column(JSONB, nullable=False, default={})
    agent_id = Column(String, ForeignKey("agent.id"), nullable=False)
    agent_config = Column(JSONB, nullable=False, default={})
    synthesizer_id = Column(String, ForeignKey("synthesizer.id"), nullable=False)
    synthesizer_config = Column(JSONB, nullable=False, default={})

