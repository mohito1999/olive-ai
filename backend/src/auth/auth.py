import jwt
from fastapi import Depends, Header
from jwt.exceptions import InvalidTokenError
from supabase._async.client import AsyncClient as Client
from supabase._async.client import create_client

from config import SUPABASE_JWT_SECRET, SUPABASE_KEY, SUPABASE_URL
from constants import UserRole
from exceptions import ForbiddenException, UnauthorizedException


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
        if not payload:
            raise UnauthorizedException(detail="Invalid token payload")
    except InvalidTokenError as e:
        raise UnauthorizedException(e, detail="Invalid token")
    return payload


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user),
):
    role = current_user.get("user_metadata", {}).get("role")
    if role != UserRole.ADMIN.value:
        raise ForbiddenException(
            f"User with id: '{current_user.get('sub')}' and role: '{role}' forbidden to perform an admin action.",
            detail="Action not allowed for this user",
        )

    return current_user
