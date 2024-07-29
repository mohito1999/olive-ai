# -*- coding: utf-8 -*-

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB

from constants import CallStatus

from .audit import AuditMixin
from .base import Base, BaseMeta


class Call(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "call"

    id = Column(
        Text,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('call')"),
    )
    organization_id = Column(Text, ForeignKey("organization.id"), nullable=False)
    campaign_id = Column(Text, ForeignKey("campaign.id"), nullable=False)
    customer_id = Column(Text, ForeignKey("customer.id"), nullable=False)
    type = Column(Text, nullable=False)
    from_number = Column(Text, nullable=False)
    to_number = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default=CallStatus.PENDING)
    retry_count = Column(Integer, nullable=False, default=0)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=False, default=0)
    recording_url = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    actions = Column(JSONB, nullable=True)

    telephony_service_id = Column(Text, ForeignKey("telephony_service.id"), nullable=False)
    telephony_service_config = Column(JSONB, nullable=False)
    transcriber_id = Column(Text, ForeignKey("transcriber.id"),nullable=False)
    transcriber_config = Column(JSONB, nullable=False, default={})
    agent_id = Column(Text, ForeignKey("agent.id"), nullable=False)
    agent_config = Column(JSONB, nullable=False, default={})
    synthesizer_id = Column(Text, ForeignKey("synthesizer.id"), nullable=False)
    synthesizer_config = Column(JSONB, nullable=False, default={})

