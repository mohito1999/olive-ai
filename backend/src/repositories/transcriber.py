from typing import Type

from models import Transcriber
from schemas import TranscriberDBInputSchema, TranscriberDBSchema

from .base import BaseRepository


class TranscriberRepository(BaseRepository[TranscriberDBInputSchema, TranscriberDBSchema, Transcriber]):
    @property
    def _in_schema(self) -> Type[TranscriberDBInputSchema]:
        return TranscriberDBInputSchema

    @property
    def _schema(self) -> Type[TranscriberDBSchema]:
        return TranscriberDBSchema

    @property
    def _table(self) -> Type[Transcriber]:
        return Transcriber

