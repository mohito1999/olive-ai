# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID

from constants import AuthProvider, UserRole

from .audit import AuditMixin
from .base import Base, BaseMeta


class User(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "user"

    id = Column(
        UUID,
        nullable=False,
        primary_key=True,  # ForeignKey("auth.users.id", ondelete="CASCADE")
    )
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    auth_provider = Column(String, nullable=False, server_default=text(AuthProvider.SUPABASE.value))
    role = Column(String, nullable=False, default=UserRole.DEFAULT)
    organization_id = Column(String, ForeignKey("organization.id"), nullable=False)

