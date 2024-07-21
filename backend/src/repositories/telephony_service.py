from typing import Type

from models import TelephonyService
from schemas import TelephonyServiceDBInputSchema, TelephonyServiceDBSchema

from .base import BaseRepository


class TelephonyServiceRepository(BaseRepository[TelephonyServiceDBInputSchema, TelephonyServiceDBSchema, TelephonyService]):
    @property
    def _in_schema(self) -> Type[TelephonyServiceDBInputSchema]:
        return TelephonyServiceDBInputSchema

    @property
    def _schema(self) -> Type[TelephonyServiceDBSchema]:
        return TelephonyServiceDBSchema

    @property
    def _table(self) -> Type[TelephonyService]:
        return TelephonyService

