from sqlalchemy import Column, ForeignKey, Text, text

from .audit import AuditMixin
from .base import Base, BaseMeta


class CampaignCustomerSet(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "campaign_customer_set"

    id = Column(
        Text,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('campaign-customer-set')"),
    )
    campaign_id = Column(Text, ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False)
    customer_set_id = Column(Text, ForeignKey("customer_set.id", ondelete="CASCADE"), nullable=False)

