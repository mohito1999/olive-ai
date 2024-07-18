from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from supabase._async.client import AsyncClient as SupabaseClient

from auth import get_current_user, get_supabase
from constants import UserRole
from exceptions import (
    ApplicationException,
    BadRequestException,
    InternalServerException,
    NotFoundException,
    RecordIntegrityException,
    RecordNotFoundException,
)
from log import log
from models import get_db
from repositories import UserRepository
from schemas import (
    RegisterRequest,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def create_user(
    payload: RegisterRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    supabase: SupabaseClient = Depends(get_supabase),
):
    try:
        # if current_user.role == UserRole.ADMIN.value:
        #     log.error("User is not an admin")

        current_user_id = "test"

        response = await supabase.auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,
                "user_metadata": {
                    "name": payload.name,
                    "organization_id": payload.organization_id,
                    "role": payload.role,
                    "created_by": current_user_id,
                    "updated_by": current_user_id,
                },
                "email_confirm": True,
            }
        )
        log.info(response.user)

        created_user = await UserRepository(db).get(auth_provider_id=response.user.id)
        return UserResponse(**created_user.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="User name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


# async def _register_user(identifier: AuthIdentifier, db: AsyncSession) -> UserDBSchema:
#     mobile_number = identifier.value
#     vua = generate_vua(mobile_number)
#     try:
#         auth_provider_id = KeycloakService.create_user(vua, mobile_number)
#     except Exception as e:
#         raise KeycloakException(str(e))
#
#     user_input_schema = UserDBInputSchema(
#         vua=vua, auth_provider_id=auth_provider_id, mobile=mobile_number
#     )
#     saved_user = await UserRepository(db).create(in_schema=user_input_schema)
#     return saved_user
#
#
# def _get_keycloak_session_id(session_id: str) -> str:
#     return session_id.split(SESSION_ID_SEPARATOR)[0]
#
#
# def _get_session_id_with_time(session_id: str) -> str:
#     return session_id + SESSION_ID_SEPARATOR + str(make_epoch(datetime_now()))
#
#
# def _is_otp_sending_allowed(user: UserDBSchema) -> bool:
#     session_id = user.session_id or ""
#     split_session_id = session_id.split(SESSION_ID_SEPARATOR)
#     if len(split_session_id) < 2:
#         # For cases where resend_at datetime is not part of session_id
#         return True
#     resend_at = epoc_to_datetime(split_session_id[1])
#     diff = abs(datetime_now() - resend_at)
#     if diff > timedelta(seconds=AUTH_RETRY_TIMEOUT):
#         return True
#     return False
#
#
# @router.post("/login", response_model=LoginResponse)
# async def login_user(login_payload: LoginRequest, db: AsyncSession = Depends(get_db)):
#     try:
#         user_repository = UserRepository(db)
#         identifier_type = login_payload.identifier.type
#         if identifier_type is AuthIdentifierType.MOBILE.value:
#             mobile_number = login_payload.identifier.value
#             vua = generate_vua(mobile_number)
#
#         elif identifier_type is AuthIdentifierType.VUA.value:
#             vua = login_payload.identifier.value
#         try:
#             user = await user_repository.get(where=[or_(User.vua == vua, User.alias_vua == vua)])
#         except RecordNotFoundException as e:
#             if login_payload.auto_register:
#                 user = await _register_user(identifier=login_payload.identifier, db=db)
#             else:
#                 raise UserNotFoundException(e)
#
#         if not _is_otp_sending_allowed(user):
#             raise TooManyRequestsException()
#         otp_data = KeycloakService.send_otp_to_user(username=user.vua, mobile_number=user.mobile)
#         log.debug(otp_data)
#
#         session_id = _get_session_id_with_time(otp_data["session_id"])
#         await user_repository.update(values={"session_id": session_id}, id=user.id)
#         EventLogger.log(EventLogSchema(event=Event.USER_LOGIN, user_id=user.id))
#         return LoginResponse(
#             identifier=login_payload.identifier,
#             otp_status=otp_data["status_description"],
#             otp_expiry=epoc_to_datetime(otp_data["expires_at"]),
#             resend_otp_at=epoc_to_datetime(otp_data["resend_at"]),
#             ref_number=session_id,
#         )
#     except ApplicationException:
#         raise
#     except Exception as e:
#         raise InternalServerException(e)
#
#
# @router.post("/register", response_model=RegisterResponse)
# async def register_user(register_payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
#     try:
#         mobile_number = register_payload.identifier.value
#         user_repository = UserRepository(db)
#
#         count = await user_repository.count(mobile=mobile_number)
#         if count != 0:
#             raise UserAlreadyExistsException()
#
#         user = await _register_user(identifier=register_payload.identifier, db=db)
#         otp_data = KeycloakService.send_otp_to_user(username=user.vua, mobile_number=mobile_number)
#         log.debug(otp_data)
#
#         session_id = _get_session_id_with_time(otp_data["session_id"])
#         await user_repository.update(values={"session_id": session_id}, id=user.id)
#         EventLogger.log(EventLogSchema(event=Event.USER_REGISTER, user_id=user.id))
#         return RegisterResponse(
#             identifier=register_payload.identifier,
#             otp_status=otp_data["status_description"],
#             otp_expiry=epoc_to_datetime(otp_data["expires_at"]),
#             resend_otp_at=epoc_to_datetime(otp_data["resend_at"]),
#             ref_number=session_id,
#         )
#     except ApplicationException:
#         raise
#     except Exception as e:
#         raise InternalServerException(e)
#
