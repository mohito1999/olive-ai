# -*- coding: utf-8 -*-
# from typing import Generator
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import ASYNC_DB_URI

engine = create_async_engine(ASYNC_DB_URI, echo=False, pool_pre_ping=True)
AsyncDBSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator:
    """
    Dependency function that yields db sessions
    """
    async with AsyncDBSession() as session:
        yield session
