from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_admin_user, get_current_user
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
from repositories import TelephonyServiceRepository
from schemas import (
    CreateTelephonyServiceRequest,
    TelephonyServiceDBInputSchema,
    TelephonyServiceResponse,
    UpdateTelephonyServiceRequest,
)

router = APIRouter()


@router.post("", response_model=TelephonyServiceResponse, status_code=201)
async def create_telephony_service(
    payload: CreateTelephonyServiceRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Creating telephony_service with name: '{payload.name}'")
        data = TelephonyServiceDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        telephony_service = await TelephonyServiceRepository(db).create(data)
        return TelephonyServiceResponse(**telephony_service.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="TelephonyService name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[TelephonyServiceResponse])
async def list_telephony_services(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        log.info("Listing telephony_services")
        items = await TelephonyServiceRepository(db).list()
        return [TelephonyServiceResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{telephony_service_id}", response_model=TelephonyServiceResponse)
async def get_telephony_service(
    telephony_service_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting telephony_service for telephony_service_id: '{telephony_service_id}'")
        item = await TelephonyServiceRepository(db).get(id=telephony_service_id)
        return TelephonyServiceResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{telephony_service_id}", response_model=TelephonyServiceResponse)
async def update_telephony_service(
    telephony_service_id: str,
    payload: UpdateTelephonyServiceRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating telephony_service for telephony_service_id: '{telephony_service_id}'")
        await TelephonyServiceRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=telephony_service_id,
        )
        telephony_service = await TelephonyServiceRepository(db).get(id=telephony_service_id)
        return TelephonyServiceResponse(**telephony_service.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="TelephonyService name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{telephony_service_id}", status_code=204)
async def delete_telephony_service(
    telephony_service_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Deleting telephony_service for telephony_service_id: '{telephony_service_id}'")
        await TelephonyServiceRepository(db).delete(
            _user_id=current_user_id, id=telephony_service_id, unique_fields=["name"]
        )
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
