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
from repositories import TranscriberRepository
from schemas import (
    CreateTranscriberRequest,
    TranscriberDBInputSchema,
    TranscriberResponse,
    UpdateTranscriberRequest,
)

router = APIRouter()


@router.post("", response_model=TranscriberResponse, status_code=201)
async def create_transcriber(
    payload: CreateTranscriberRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Creating transcriber with name: '{payload.name}'")
        data = TranscriberDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        transcriber = await TranscriberRepository(db).create(data)
        return TranscriberResponse(**transcriber.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Transcriber name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[TranscriberResponse])
async def list_transcribers(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        log.info("Listing transcribers")
        items = await TranscriberRepository(db).list()
        return [TranscriberResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{transcriber_id}", response_model=TranscriberResponse)
async def get_transcriber(
    transcriber_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting transcriber for transcriber_id: '{transcriber_id}'")
        item = await TranscriberRepository(db).get(id=transcriber_id)
        return TranscriberResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{transcriber_id}", response_model=TranscriberResponse)
async def update_transcriber(
    transcriber_id: str,
    payload: UpdateTranscriberRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating transcriber for transcriber_id: '{transcriber_id}'")
        transcriber = await TranscriberRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=transcriber_id,
        )
        return TranscriberResponse(**transcriber.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Transcriber name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{transcriber_id}", status_code=204)
async def delete_transcriber(
    transcriber_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Deleting transcriber for transcriber_id: '{transcriber_id}'")
        await TranscriberRepository(db).delete(id=transcriber_id, unique_fields=["name"])
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
