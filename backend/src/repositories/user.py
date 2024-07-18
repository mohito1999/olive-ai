# -*- coding: utf-8 -*-
from typing import Type

from models import User
from schemas import UserDBInputSchema, UserDBSchema

from .base import BaseRepository


class UserRepository(BaseRepository[UserDBInputSchema, UserDBSchema, User]):
    @property
    def _in_schema(self) -> Type[UserDBInputSchema]:
        return UserDBInputSchema

    @property
    def _schema(self) -> Type[UserDBSchema]:
        return UserDBSchema

    @property
    def _table(self) -> Type[User]:
        return User

