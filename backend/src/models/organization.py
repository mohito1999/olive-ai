# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB

from .audit import AuditMixin
from .base import Base, BaseMeta


class Organization(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "organization"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('organization')"),
    )
    name = Column(String, nullable=True)
    credits = Column(Integer, nullable=False, default=0)
    telephony_service_id = Column(String, ForeignKey("telephony_service.id"), nullable=False)
    telephony_service_config = Column(JSONB, nullable=False)
    transcriber_id = Column(String, ForeignKey("transcriber.id"),nullable=False)
    transcriber_config = Column(JSONB, nullable=False, default={})
    agent_id = Column(String, ForeignKey("agent.id"), nullable=False)
    agent_config = Column(JSONB, nullable=False, default={})
    synthesizer_id = Column(String, ForeignKey("synthesizer.id"), nullable=False)
    synthesizer_config = Column(JSONB, nullable=False, default={})

