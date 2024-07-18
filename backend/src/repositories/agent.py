from typing import Type

from models import Agent
from schemas import AgentDBInputSchema, AgentDBSchema

from .base import BaseRepository


class AgentRepository(BaseRepository[AgentDBInputSchema, AgentDBSchema, Agent]):
    @property
    def _in_schema(self) -> Type[AgentDBInputSchema]:
        return AgentDBInputSchema

    @property
    def _schema(self) -> Type[AgentDBSchema]:
        return AgentDBSchema

    @property
    def _table(self) -> Type[Agent]:
        return Agent

