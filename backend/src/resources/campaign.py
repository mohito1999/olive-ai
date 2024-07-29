from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from constants import (
    CallStatus,
    CallType,
)
from exceptions import (
    ApplicationException,
    BadRequestException,
    InternalServerException,
    NotFoundException,
    RecordIntegrityException,
    RecordNotFoundException,
)
from jobs import make_outbound_call_task
from log import log
from models import get_db
from repositories import (
    AgentRepository,
    CallRepository,
    CampaignCustomerSetRepository,
    CampaignRepository,
    CustomerRepository,
    OrganizationRepository,
    SynthesizerRepository,
    TelephonyServiceRepository,
    TranscriberRepository,
)
from schemas import (
    CallDBInputSchema,
    CampaignCustomerSetDBInputSchema,
    CampaignDBInputSchema,
    CampaignResponse,
    CreateCampaignRequest,
    TestCampaignRequest,
    TestCampaignResponse,
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
        item = await CampaignRepository(db).get(id=campaign_id, organization_id=current_user_organization_id)
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

        campaign = await CampaignRepository(db).get(id=campaign_id, organization_id=current_user_organization_id)

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

        campaign = await CampaignRepository(db).update(
            values={
                **{
                    **payload.dict(exclude_none=True, exclude="customer_sets"),
                    "updated_by": current_user_id,
                }
            },
            id=campaign_id,
        )
        return CampaignResponse(**campaign.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.post("/{campaign_id}/test", response_model=TestCampaignResponse)
async def test_campaign(
    campaign_id: str,
    payload: TestCampaignRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")

    try:
        log.info(f"Testing campaign_id: '{campaign_id}'")

        campaign = await CampaignRepository(db).get(id=campaign_id, organization_id=current_user_organization_id)
        if campaign.organization_id != current_user_organization_id:
            raise BadRequestException(
                detail=f"User does not belong to organization with id: '{campaign.organization_id}'"
            )

        organization = await OrganizationRepository(db).get(id=campaign.organization_id)

        telephony_service_id = organization.telephony_service_id
        telephony_service_config = organization.telephony_service_config
        agent_id = organization.agent_id
        agent_config = organization.agent_config
        transcriber_id = organization.transcriber_id
        transcriber_config = organization.transcriber_config
        synthesizer_id = organization.synthesizer_id
        synthesizer_config = organization.synthesizer_config

        if campaign.telephony_service_id:
            telephony_service_id = campaign.telephony_service_id
            telephony_service_config = campaign.telephony_service_config

        if campaign.agent_id:
            agent_id = campaign.agent_id
            agent_config = campaign.agent_config

        if campaign.transcriber_id:
            transcriber_id = campaign.transcriber_id
            transcriber_config = campaign.transcriber_config

        if campaign.synthesizer_id:
            synthesizer_id = campaign.synthesizer_id
            synthesizer_config = campaign.synthesizer_config

        telephony_service = await TelephonyServiceRepository(db).get(id=telephony_service_id)
        agent = await AgentRepository(db).get(id=agent_id)
        transcriber = await TranscriberRepository(db).get(id=transcriber_id)
        synthesizer = await SynthesizerRepository(db).get(id=synthesizer_id)

        telephony_service_config = {**telephony_service.config, **telephony_service_config}
        agent_config = {**agent.config, **agent_config}
        transcriber_config = {**transcriber.config, **transcriber_config}
        synthesizer_config = {**synthesizer.config, **synthesizer_config}

        outbound_caller_number = telephony_service_config.pop("outbound_caller_number")
        customer = await CustomerRepository(db).get(id=payload.customer_id, organization_id=current_user_organization_id)

        call = await CallRepository(db).create(
            CallDBInputSchema(
                organization_id=campaign.organization_id,
                campaign_id=campaign.id,
                customer_id=customer.id,
                type=CallType.OUTBOUND.value,
                from_number=outbound_caller_number,
                to_number=customer.mobile_number,
                status=CallStatus.PENDING.value,
                retry_count=0,
                telephony_service_id=telephony_service_id,
                telephony_service_config=telephony_service_config,
                agent_id=agent_id,
                agent_config=agent_config,
                transcriber_id=transcriber_id,
                transcriber_config=transcriber_config,
                synthesizer_id=synthesizer_id,
                synthesizer_config=synthesizer_config,
                created_by=current_user_id,
                updated_by=current_user_id,
            )
        )

        make_outbound_call_task.apply_async((call.id,))
        return TestCampaignResponse(call_id=call.id, message="Call queued successfully")
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
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Deleting campaign_id: '{campaign_id}'")
        await CampaignRepository(db).delete(id=campaign_id, organization_id=current_user_organization_id)
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
