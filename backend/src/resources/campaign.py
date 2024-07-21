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
from repositories import CampaignRepository
from schemas import (
    CampaignDBInputSchema,
    CampaignResponse,
    CreateCampaignRequest,
    UpdateCampaignRequest,
)

router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    payload: CreateCampaignRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Creating campaign with name: '{payload.name}'")
        data = CampaignDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        campaign = await CampaignRepository(db).create(data)
        return CampaignResponse(**campaign.dict())
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        log.info("Listing campaigns")
        items = await CampaignRepository(db).list()
        return [CampaignResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting campaign for campaign_id: '{campaign_id}'")
        item = await CampaignRepository(db).get(id=campaign_id)
        return CampaignResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    payload: UpdateCampaignRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating campaign for campaign_id: '{campaign_id}'")
        campaign = await CampaignRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=campaign_id,
        )
        return CampaignResponse(**campaign.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Deleting campaign for campaign_id: '{campaign_id}'")
        await CampaignRepository(db).delete(id=campaign_id)
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
