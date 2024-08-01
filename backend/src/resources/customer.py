from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
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
from repositories import CustomerRepository, OrganizationRepository
from schemas import (
    CreateCustomerRequest,
    CustomerDBInputSchema,
    CustomerResponse,
    UpdateCustomerRequest,
)

router = APIRouter()


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(
    payload: CreateCustomerRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")

    try:
        log.info(f"Creating customer with name: '{payload.name}'")
        organization_id = payload.organization_id

        if organization_id != current_user_organization_id:
            raise BadRequestException(
                f"User does not belong to organization with id: '{organization_id}'"
            )

        try:
            await OrganizationRepository(db).get(id=organization_id)
            log.info(f"Organization with id: '{organization_id}' exists")
        except RecordNotFoundException:
            raise NotFoundException("Organization not found")

        data = CustomerDBInputSchema(
            **{**payload.dict(), "updated_by": current_user_id, "created_by": current_user_id}
        )
        customer = await CustomerRepository(db).create(data)
        return CustomerResponse(**customer.dict())
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Customer name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    customer_set_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info("Listing customers")
        q = {"organization_id": current_user_organization_id}
        if customer_set_id:
            q["customer_set_id"] = customer_set_id
        items = await CustomerRepository(db).list(**q)
        return [CustomerResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Getting customer for customer_id: '{customer_id}'")
        item = await CustomerRepository(db).get(
            id=customer_id, organization_id=current_user_organization_id
        )
        return CustomerResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    payload: UpdateCustomerRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Updating customer for customer_id: '{customer_id}'")
        await CustomerRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=customer_id,
            organization_id=current_user_organization_id,
        )
        customer = await CustomerRepository(db).get(id=customer_id)
        return CustomerResponse(**customer.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except RecordIntegrityException as e:
        raise BadRequestException(e, detail="Customer name already exists")
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")
    try:
        log.info(f"Deleting customer for customer_id: '{customer_id}'")
        await CustomerRepository(db).delete(
            _user_id=current_user_id,
            id=customer_id,
            organization_id=current_user_organization_id,
            unique_fields=["name"],
        )
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
