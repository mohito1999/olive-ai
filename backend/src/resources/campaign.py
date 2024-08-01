from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from constants import CallStatus, CampaignAction, CampaignStatus
from exceptions import (
    ApplicationException,
    BadRequestException,
    InternalServerException,
    NotFoundException,
    RecordIntegrityException,
    RecordNotFoundException,
)
from jobs import execute_campaign_task
from log import log
from models import get_db
from repositories import (
    CallRepository,
    CampaignCustomerSetRepository,
    CampaignRepository,
    CustomerRepository,
    OrganizationRepository,
)
from schemas import (
    CampaignCustomerSetDBInputSchema,
    CampaignDBInputSchema,
    CampaignDBNoRelSchema,
    CampaignResponse,
    CreateCampaignRequest,
    ExecuteCampaignRequest,
    ExecuteCampaignResponse,
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
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")

    try:
        log.info(f"Creating campaign with name: '{payload.name}'")
        if payload.organization_id != current_user_organization_id:
            raise BadRequestException(
                detail=f"User does not belong to organization with id: '{payload.organization_id}'"
            )

        try:
            await OrganizationRepository(db).get(id=payload.organization_id)
            log.info(f"Organization with id: '{payload.organization_id}' exists")
        except RecordNotFoundException:
            raise NotFoundException(detail="Organization not found")

        data = CampaignDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        campaign = await CampaignRepository(db).create(data)

        try:
            log.info(f"Creating campaign customer set for campaign_id: '{campaign.id}'")
            if payload.customer_sets is not None:
                entries = [
                    CampaignCustomerSetDBInputSchema(
                        campaign_id=campaign.id,
                        customer_set_id=customer_set_id,
                        created_by=current_user_id,
                        updated_by=current_user_id,
                    )
                    for customer_set_id in payload.customer_sets
                ]
                if len(entries) > 0:
                    await CampaignCustomerSetRepository(db).bulk_create(entries)
        except RecordIntegrityException as e:
            raise BadRequestException(e, detail="Customer set not found")

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
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info("Listing campaigns")
        items = await CampaignRepository(db).list(organization_id=current_user_organization_id)
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
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Getting campaign for campaign_id: '{campaign_id}'")
        item = await CampaignRepository(db).get(
            id=campaign_id, organization_id=current_user_organization_id
        )
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
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Updating campaign_id: '{campaign_id}'")

        campaign = await CampaignRepository(db).get(
            id=campaign_id, organization_id=current_user_organization_id
        )

        if payload.customer_sets is not None:
            await CampaignCustomerSetRepository(db).delete(
                campaign_id=campaign_id, permanent_operation=True
            )
            entries = [
                CampaignCustomerSetDBInputSchema(
                    campaign_id=campaign_id,
                    customer_set_id=customer_set_id,
                    created_by=current_user_id,
                    updated_by=current_user_id,
                )
                for customer_set_id in payload.customer_sets
            ]
            if len(entries) > 0:
                await CampaignCustomerSetRepository(db).bulk_create(entries)

        await CampaignRepository(db).update(
            values={
                **{
                    **payload.dict(exclude_none=True, exclude="customer_sets"),
                    "updated_by": current_user_id,
                }
            },
            id=campaign_id,
        )
        campaign = await CampaignRepository(db).get(id=campaign_id)
        return CampaignResponse(**campaign.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.post("/{campaign_id}/execute", response_model=ExecuteCampaignResponse)
async def execute_campaign(
    campaign_id: str,
    payload: ExecuteCampaignRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")

    try:
        campaign = await CampaignRepository(db).get(
            id=campaign_id, organization_id=current_user_organization_id
        )

        if payload.action == CampaignAction.TEST.value:
            if payload.customer_id is None:
                raise BadRequestException(detail="Customer ID is required to test campaign")
            log.info(f"Testing campaign_id: '{campaign_id}'")
            customer = await CustomerRepository(db).get(
                id=payload.customer_id, organization_id=current_user_organization_id
            )
            execute_campaign_task.apply_async(
                (
                    campaign.id,
                    customer.id,
                )
            )
            return ExecuteCampaignResponse(message="Call queued successfully")

        elif payload.action == CampaignAction.START.value:
            if campaign.status == CampaignStatus.RUNNING.value:
                raise BadRequestException(detail="Campaign already running")

            log.info(f"Starting campaign_id: '{campaign_id}'")
            execute_campaign_task.apply_async((campaign.id,))

            campaign.status = CampaignStatus.RUNNING.value
            campaign.updated_by = current_user_id
            await CampaignRepository(db).update(
                CampaignDBNoRelSchema(**campaign.dict()), id=campaign.id
            )

            return ExecuteCampaignResponse(message="Campaign started successfully")

        elif payload.action == CampaignAction.STOP.value:
            if campaign.status == CampaignStatus.IDLE.value:
                raise BadRequestException(detail="Campaign already idle")

            log.info(f"Stopping campaign_id: '{campaign_id}'")
            try:
                await CallRepository(db).update(
                    values={"status": CallStatus.CANCELLED.value, "updated_by": current_user_id},
                    campaign_id=campaign_id,
                    status=CallStatus.PENDING.value,
                )
            except RecordNotFoundException:
                pass

            campaign.status = CampaignStatus.IDLE.value
            campaign.updated_by = current_user_id
            await CampaignRepository(db).update(
                CampaignDBNoRelSchema(**campaign.dict()), id=campaign.id
            )
            return ExecuteCampaignResponse(message="Campaign stopped successfully")

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
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Deleting campaign-customer-set mapping for campaign_id: '{campaign_id}'")
        try:
            await CampaignCustomerSetRepository(db).delete(
                campaign_id=campaign_id, permanent_operation=True
            )
        except RecordNotFoundException:
            pass
        log.info(f"Deleting campaign_id: '{campaign_id}'")
        await CampaignRepository(db).delete(
            _user_id=current_user_id, id=campaign_id, organization_id=current_user_organization_id
        )
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
