from typing import Type

from models import Synthesizer
from schemas import SynthesizerDBInputSchema, SynthesizerDBSchema

from .base import BaseRepository


class SynthesizerRepository(BaseRepository[SynthesizerDBInputSchema, SynthesizerDBSchema, Synthesizer]):
    @property
    def _in_schema(self) -> Type[SynthesizerDBInputSchema]:
        return SynthesizerDBInputSchema

    @property
    def _schema(self) -> Type[SynthesizerDBSchema]:
        return SynthesizerDBSchema

    @property
    def _table(self) -> Type[Synthesizer]:
        return Synthesizer

