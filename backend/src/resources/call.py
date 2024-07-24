from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from exceptions import (
    ApplicationException,
    InternalServerException,
    NotFoundException,
    RecordNotFoundException,
)
from log import log
from models import get_db
from repositories import CallRepository
from schemas import (
    CallResponse,
)

router = APIRouter()


@router.get("", response_model=List[CallResponse])
async def list_calls(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info("Listing calls")
        q = {"organization_id": current_user_organization_id}
        items = await CallRepository(db).list(**q)
        return [CallResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Getting call_id: '{call_id}'")
        item = await CallRepository(db).get(id=call_id, organization_id=current_user_organization_id)
        return CallResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)

