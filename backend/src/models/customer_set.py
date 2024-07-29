# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Text, text

from .audit import AuditMixin
from .base import Base, BaseMeta


class CustomerSet(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "customer_set"

    id = Column(
        Text,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('customer-set')"),
    )
    organization_id = Column(Text, ForeignKey("organization.id"), nullable=False)
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    url = Column(Text, nullable=True)

