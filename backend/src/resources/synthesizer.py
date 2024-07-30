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
from repositories import SynthesizerRepository
from schemas import (
    CreateSynthesizerRequest,
    SynthesizerDBInputSchema,
    SynthesizerResponse,
    UpdateSynthesizerRequest,
)

router = APIRouter()


@router.post("", response_model=SynthesizerResponse, status_code=201)
async def create_synthesizer(
    payload: CreateSynthesizerRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Creating synthesizer with name: '{payload.name}'")
        data = SynthesizerDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        synthesizer = await SynthesizerRepository(db).create(data)
        return SynthesizerResponse(**synthesizer.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Synthesizer name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[SynthesizerResponse])
async def list_synthesizers(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        log.info("Listing synthesizers")
        items = await SynthesizerRepository(db).list()
        return [SynthesizerResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{synthesizer_id}", response_model=SynthesizerResponse)
async def get_synthesizer(
    synthesizer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting synthesizer for synthesizer_id: '{synthesizer_id}'")
        item = await SynthesizerRepository(db).get(id=synthesizer_id)
        return SynthesizerResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{synthesizer_id}", response_model=SynthesizerResponse)
async def update_synthesizer(
    synthesizer_id: str,
    payload: UpdateSynthesizerRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating synthesizer for synthesizer_id: '{synthesizer_id}'")
        synthesizer = await SynthesizerRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=synthesizer_id,
        )
        return SynthesizerResponse(**synthesizer.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Synthesizer name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{synthesizer_id}", status_code=204)
async def delete_synthesizer(
    synthesizer_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Deleting synthesizer for synthesizer_id: '{synthesizer_id}'")
        await SynthesizerRepository(db).delete(id=synthesizer_id, unique_fields=["name"])
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
