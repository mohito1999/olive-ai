# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, String, text

from constants import AuthProvider, UserRole

from .audit import AuditMixin
from .base import Base, BaseMeta


class User(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "user"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('user')"),
    )
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    auth_provider = Column(String, nullable=False, default=AuthProvider.SUPABASE)
    auth_provider_id = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.DEFAULT)
    organization_id = Column(String, ForeignKey("organization.id"), nullable=False)

