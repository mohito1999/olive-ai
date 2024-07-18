# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import JSONB

from .audit import AuditMixin
from .base import Base, BaseMeta


class TelephonyService(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "telephony_service"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('telephony-service')"),
    )
    name = Column(String, nullable=False, unique=True)
    config = Column(JSONB, nullable=False, default={})

