from typing import Type

from models import Organization
from schemas import OrganizationDBInputSchema, OrganizationDBSchema

from .base import BaseRepository


class OrganizationRepository(BaseRepository[OrganizationDBInputSchema, OrganizationDBSchema, Organization]):
    @property
    def _in_schema(self) -> Type[OrganizationDBInputSchema]:
        return OrganizationDBInputSchema

    @property
    def _schema(self) -> Type[OrganizationDBSchema]:
        return OrganizationDBSchema

    @property
    def _table(self) -> Type[Organization]:
        return Organization
