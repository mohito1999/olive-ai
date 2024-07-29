#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Define an Abstract Base Class (ABC) for models
"""
from datetime import datetime
from weakref import WeakValueDictionary

from sqlalchemy import Column, DateTime, Text, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta, as_declarative
from sqlalchemy.orm import aliased

from log import log


class BaseMeta(DeclarativeMeta):
    """Define a metaclass for the BaseModel
    Implement `__getitem__` for managing aliases"""

    def __init__(cls, *args):
        super().__init__(*args)
        cls.aliases = WeakValueDictionary()

    def __getitem__(cls, key):
        try:
            alias = cls.aliases[key]
        except KeyError:
            alias = aliased(cls)
            cls.aliases[key] = alias
        return alias


@as_declarative()
class Base:
    __name__: str
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        Text,
        nullable=False,
        primary_key=True,
        server_default=text("id_generator()"),
    )
    deleted_at = Column(DateTime)

    print_filter = ()

    def __repr__(self):
        """Define a base way to print models
        Columns inside `print_filter` are excluded"""
        return "%s(%s)" % (
            self.__class__.__name__,
            {
                column: value
                for column, value in self._to_dict().items()
                if column not in self.print_filter
            },
        )

    async def save(self, db: AsyncSession):
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self

    async def delete(self, db: AsyncSession, unique_fields: list[str] = []):
        now = datetime.utcnow()
        now_str = now.strftime("%Y%m%d%H%M%S")
        self.deleted_at = now
        for key in unique_fields:
            val = getattr(self, key)
            log.info(val)
            if val is not None:
                setattr(self, key, val+f"__{now_str}")
        db.add(self)
        await db.commit()
        await db.refresh(self)
