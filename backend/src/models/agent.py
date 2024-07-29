# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text, text
from sqlalchemy.dialects.postgresql import JSONB

from .audit import AuditMixin
from .base import Base, BaseMeta


class Agent(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "agent"

    id = Column(
        Text,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('agent')"),
    )
    name = Column(Text, nullable=False, unique=True)
    config = Column(JSONB, nullable=False, default={})

