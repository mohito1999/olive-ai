from typing import Type

from models import Customer
from schemas import CustomerDBInputSchema, CustomerDBSchema

from .base import BaseRepository


class CustomerRepository(BaseRepository[CustomerDBInputSchema, CustomerDBSchema, Customer]):
    @property
    def _in_schema(self) -> Type[CustomerDBInputSchema]:
        return CustomerDBInputSchema

    @property
    def _schema(self) -> Type[CustomerDBSchema]:
        return CustomerDBSchema

    @property
    def _table(self) -> Type[Customer]:
        return Customer

