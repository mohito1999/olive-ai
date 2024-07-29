# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID

from constants import AuthProvider, UserRole

from .audit import AuditMixin
from .base import Base, BaseMeta


class User(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "user"

    id = Column(
        UUID,
        # ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    mobile_number = Column(Text, nullable=True)
    auth_provider = Column(
        Text, nullable=False, server_default=text(AuthProvider.SUPABASE.value)
    )
    role = Column(Text, nullable=False, default=UserRole.DEFAULT)
    organization_id = Column(Text, ForeignKey("organization.id"), nullable=False)
