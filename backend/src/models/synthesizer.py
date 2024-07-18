# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import JSONB

from .audit import AuditMixin
from .base import Base, BaseMeta


class Synthesizer(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "synthesizer"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('synthesizer')"),
    )
    name = Column(String, nullable=False, unique=True)
    config = Column(JSONB, nullable=False, default={})

