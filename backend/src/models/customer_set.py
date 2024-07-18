# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, String, text

from .audit import AuditMixin
from .base import Base, BaseMeta


class CustomerSet(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "customer_set"

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('customer-set')"),
    )
    organization_id = Column(String, ForeignKey("organization.id"), nullable=False)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=True)

