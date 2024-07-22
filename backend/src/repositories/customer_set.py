from typing import Type

from models import CustomerSet
from schemas import CustomerSetDBInputSchema, CustomerSetDBSchema

from .base import BaseRepository


class CustomerSetRepository(BaseRepository[CustomerSetDBInputSchema, CustomerSetDBSchema, CustomerSet]):
    @property
    def _in_schema(self) -> Type[CustomerSetDBInputSchema]:
        return CustomerSetDBInputSchema

    @property
    def _schema(self) -> Type[CustomerSetDBSchema]:
        return CustomerSetDBSchema

    @property
    def _table(self) -> Type[CustomerSet]:
        return CustomerSet

