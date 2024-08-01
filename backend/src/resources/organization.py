from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_admin_user
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
from repositories import OrganizationRepository
from schemas import (
    CreateOrganizationRequest,
    OrganizationDBInputSchema,
    OrganizationResponse,
    UpdateOrganizationRequest,
)

router = APIRouter()


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    payload: CreateOrganizationRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Creating organization with name: '{payload.name}'")
        data = OrganizationDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        organization = await OrganizationRepository(db).create(data)
        return OrganizationResponse(**organization.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Organization name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    try:
        log.info("Listing organizations")
        items = await OrganizationRepository(db).list()
        return [OrganizationResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting organization for organization_id: '{organization_id}'")
        item = await OrganizationRepository(db).get(id=organization_id)
        return OrganizationResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    payload: UpdateOrganizationRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating organization for organization_id: '{organization_id}'")
        await OrganizationRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=organization_id,
        )
        organization = await OrganizationRepository(db).get(id=organization_id)
        return OrganizationResponse(**organization.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Organization name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{organization_id}", status_code=204)
async def delete_organization(
    organization_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Deleting organization for organization_id: '{organization_id}'")
        await OrganizationRepository(db).delete(_user_id=current_user_id, id=organization_id)
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
