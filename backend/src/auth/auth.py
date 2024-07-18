import jwt
from fastapi import Header
from jwt.exceptions import InvalidTokenError
from supabase._async.client import AsyncClient as Client
from supabase._async.client import create_client

from config import SUPABASE_JWT_SECRET, SUPABASE_KEY, SUPABASE_URL
from exceptions import UnauthorizedException
from log import log


async def get_supabase() -> Client:
    return await create_client(SUPABASE_URL, SUPABASE_KEY)


async def get_current_user(
    auth_header: str = Header(None, alias="Authorization"),
):
    if not auth_header:
        raise UnauthorizedException(detail="No token provided")

    split_header = auth_header.split(" ")
    if len(split_header) != 2:
        raise UnauthorizedException(detail="Invalid token format")

    token = split_header[1]
    try:
        payload = jwt.decode(
            token, key=SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated"
        )
        log.info(payload)
    except InvalidTokenError as e:
        raise UnauthorizedException(e, detail="Invalid token")
    return payload
