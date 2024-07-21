from typing import Type

from models import Campaign
from schemas import CampaignDBInputSchema, CampaignDBSchema

from .base import BaseRepository


class CampaignRepository(BaseRepository[CampaignDBInputSchema, CampaignDBSchema, Campaign]):
    @property
    def _in_schema(self) -> Type[CampaignDBInputSchema]:
        return CampaignDBInputSchema

    @property
    def _schema(self) -> Type[CampaignDBSchema]:
        return CampaignDBSchema

    @property
    def _table(self) -> Type[Campaign]:
        return Campaign

