from typing import Type

from models import Call
from schemas import CallDBInputSchema, CallDBSchema

from .base import BaseRepository


class CallRepository(BaseRepository[CallDBInputSchema, CallDBSchema, Call]):
    @property
    def _in_schema(self) -> Type[CallDBInputSchema]:
        return CallDBInputSchema

    @property
    def _schema(self) -> Type[CallDBSchema]:
        return CallDBSchema

    @property
    def _table(self) -> Type[Call]:
        return Call
