from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from exceptions import (
    ApplicationException,
    InternalServerException,
    NotFoundException,
    RecordNotFoundException,
)
from log import log
from models import Call, get_db
from repositories import CallRepository
from schemas import (
    CallResponse,
    CallTranscriptResponse,
    ListCallsResponse,
)

router = APIRouter()


@router.get("", response_model=List[ListCallsResponse])
async def list_calls(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info("Listing calls")
        q = {"organization_id": current_user_organization_id}
        items = await CallRepository(db).list(
            **q, order_by=[Call.created_at.desc()], limit=limit, offset=offset
        )
        return [ListCallsResponse(**item.dict()) for item in items]
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
        item = await CallRepository(db).get(
            id=call_id, organization_id=current_user_organization_id
        )
        return CallResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{call_id}/transcript", response_model=CallTranscriptResponse)
async def get_call_transcript(
    call_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Getting call_id: '{call_id}'")
        item = await CallRepository(db).get(
            id=call_id, organization_id=current_user_organization_id
        )
        return CallTranscriptResponse(transcript=item.transcript)
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
