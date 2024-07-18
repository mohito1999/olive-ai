from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    ApplicationException,
    InternalServerException,
)
from log import log
from models import get_db
from repositories import OrganizationRepository
from schemas import (
    CreateOrganizationRequest,
    OrganizationDBInputSchema,
    OrganizationResponse,
)

router = APIRouter()


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    request: CreateOrganizationRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Creating organization with name: {request.name}")
        data = OrganizationDBInputSchema(
            **{**request.dict(), "updated_by": "test", "created_by": "test"}
        )
        org = await OrganizationRepository(db).create(data)
        return OrganizationResponse(**org.dict())
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info("Listing organizations")
        items = await OrganizationRepository(db).list()
        return [OrganizationResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


# @router.get("/{organization_id}", response_model=OrganizationResponse)
# async def get_organization(
#     organization_id: str,
#     user_id: str = Header(..., alias="x-user-id"),
# ):
#     try:
#         log.info(
#             f"Getting organization for user_id: {user_id}, organization_id: {organization_id}"
#         )
#         item = OrganizationRepository().get(user_id, organization_id)
#         return OrganizationResponse(**item.dict())
#     except RecordNotFoundException as e:
#         raise NotFoundException(e)
#     except ApplicationException as e:
#         raise e
#     except Exception as e:
#         raise InternalServerException(e)
#
#
# @router.patch("/{organization_id}", response_model=OrganizationResponse)
# async def update_organization(
#     organization_id: str,
#     request: UpdateOrganizationRequest,
#     user_id: str = Header(..., alias="x-user-id"),
# ):
#     try:
#         log.info(
#             f"Updating organization for user_id: {user_id}, organization_id: {organization_id}"
#         )
#         item = OrganizationRepository().update(request, user_id, organization_id)
#         return OrganizationResponse(**item.dict())
#     except RecordNotFoundException as e:
#         raise NotFoundException(e)
#     except ApplicationException as e:
#         raise e
#     except Exception as e:
#         raise InternalServerException(e)
#
#
# @router.delete("/{organization_id}", status_code=204)
# async def delete_organization(
#     organization_id: str,
#     user_id: str = Header(..., alias="x-user-id"),
# ):
#     try:
#         log.info(
#             f"Deleting organization for user_id: {user_id}, organization_id: {organization_id}"
#         )
#         OrganizationRepository().delete(user_id, organization_id)
#     except RecordNotFoundException as e:
#         raise NotFoundException(e)
#     except ApplicationException as e:
#         raise e
#     except Exception as e:
#         raise InternalServerException(e)
