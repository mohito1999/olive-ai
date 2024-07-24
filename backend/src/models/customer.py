# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB

from .audit import AuditMixin
from .base import Base, BaseMeta


class Customer(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "customer"
    __table_args__ = (
        UniqueConstraint("customer_set_id", "mobile_number", name="customer_set_id_mobile_number_uc"),
    )

    id = Column(
        String,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('customer')"),
    )
    organization_id = Column(String, ForeignKey("organization.id"), nullable=False)
    customer_set_id = Column(String, ForeignKey("customer_set.id"), nullable=True)
    name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    customer_metadata = Column(JSONB, nullable=False, default={})

