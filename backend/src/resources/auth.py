from fastapi import APIRouter, Depends
from gotrue.errors import AuthApiError
from sqlalchemy.ext.asyncio import AsyncSession
from supabase._async.client import AsyncClient as SupabaseClient

from auth import get_current_admin_user, get_supabase
from exceptions import (
    ApplicationException,
    BadRequestException,
    InternalServerException,
    NotFoundException,
    RecordNotFoundException,
)
from log import log
from models import get_db
from repositories import OrganizationRepository, UserRepository
from schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def create_user(
    payload: RegisterRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    supabase: SupabaseClient = Depends(get_supabase),
):
    try:
        current_user_id = current_user.get("sub")
        log.info(f"Creating user with email: '{payload.email}'")
        try:
            await OrganizationRepository(db).get(id=payload.organization_id)
            log.info(f"Organization with id: '{payload.organization_id}' exists")
        except RecordNotFoundException:
            raise NotFoundException("Organization not found")

        try:
            response = await supabase.auth.admin.create_user(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "user_metadata": {
                        "display_name": payload.name,
                        "organization_id": payload.organization_id,
                        "role": payload.role,
                        "created_by": current_user_id,
                    },
                    "email_confirm": True,
                }
            )
            log.info(
                f"User with email: '{payload.email}' created successfully. (id: '{response.user.id}')"
            )
        except AuthApiError as e:
            raise BadRequestException(e, detail=e.message)

        # User is created automatically through an SQL trigger
        created_user = await UserRepository(db).get(id=response.user.id)
        return UserResponse(**created_user.dict())
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.post("/login", response_model=LoginResponse, status_code=201)
async def login_user(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    supabase: SupabaseClient = Depends(get_supabase),
):
    try:
        log.info(f"Logging in user with email: '{payload.email}'")
        try:
            response = await supabase.auth.sign_in_with_password(
                {"email": payload.email, "password": payload.password}
            )
        except AuthApiError as e:
            raise BadRequestException(e, detail=e.message)
        user = response.user
        session = response.session
        display_name = user.user_metadata.get("display_name", "")

        return LoginResponse(
            id=user.id,
            name=display_name,
            access_token=session.access_token,
            expires_in=session.expires_in,
            refresh_token=session.refresh_token,
        )
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
