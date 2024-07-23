from typing import Type

from models import CampaignCustomerSet
from schemas import CampaignCustomerSetDBInputSchema, CampaignCustomerSetDBSchema

from .base import BaseRepository


class CampaignCustomerSetRepository(BaseRepository[CampaignCustomerSetDBInputSchema, CampaignCustomerSetDBSchema, CampaignCustomerSet]):
    @property
    def _in_schema(self) -> Type[CampaignCustomerSetDBInputSchema]:
        return CampaignCustomerSetDBInputSchema

    @property
    def _schema(self) -> Type[CampaignCustomerSetDBSchema]:
        return CampaignCustomerSetDBSchema

    @property
    def _table(self) -> Type[CampaignCustomerSet]:
        return CampaignCustomerSet

