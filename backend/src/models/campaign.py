from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from constants import CampaignStatus, CampaignType

from .audit import AuditMixin
from .base import Base, BaseMeta
from .campaign_customer_set import CampaignCustomerSet


class Campaign(Base, AuditMixin, metaclass=BaseMeta):
    __tablename__ = "campaign"

    id = Column(
        Text,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator('campaign')"),
    )
    organization_id = Column(Text, ForeignKey("organization.id"), nullable=False)
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=False, default=CampaignType.OUTBOUND)
    status = Column(Text, nullable=False, server_default=CampaignStatus.DRAFT.value)
    prompt = Column(Text, nullable=False)
    initial_message = Column(Text, nullable=False)
    max_duration = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=0)
    end_date = Column(DateTime, nullable=True)

    # Overrides
    telephony_service_id = Column(Text, ForeignKey("telephony_service.id"), nullable=True)
    telephony_service_config = Column(JSONB, nullable=True)
    transcriber_id = Column(Text, ForeignKey("transcriber.id"),nullable=True)
    transcriber_config = Column(JSONB, nullable=True)
    agent_id = Column(Text, ForeignKey("agent.id"), nullable=True)
    agent_config = Column(JSONB, nullable=True)
    synthesizer_id = Column(Text, ForeignKey("synthesizer.id"), nullable=True)
    synthesizer_config = Column(JSONB, nullable=True)

    customer_sets = relationship(
        "CustomerSet",
        secondary=CampaignCustomerSet.__table__,
        lazy="selectin",
    )

