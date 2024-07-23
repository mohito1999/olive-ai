from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from supabase._async.client import AsyncClient as SupabaseClient

from auth import get_current_user, get_supabase
from config import SUPABASE_CUSTOMER_SET_BUCKET_NAME
from constants import CustomerSetStatus, CustomerSetType
from exceptions import (
    ApplicationException,
    BadRequestException,
    InternalServerException,
    NotFoundException,
    RecordNotFoundException,
)
from jobs import process_csv_file_task
from log import log
from models import get_db
from repositories import CustomerSetRepository, OrganizationRepository
from schemas import (
    CreateCustomerSetRequest,
    CustomerSetDBInputSchema,
    CustomerSetResponse,
    ProcessCustomerSetResponse,
    UpdateCustomerSetRequest,
)

router = APIRouter()


@router.post("", response_model=CustomerSetResponse, status_code=201)
async def create_customer_set(
    organization_id: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    type: CustomerSetType = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    supabase: SupabaseClient = Depends(get_supabase),
):
    current_user_id = current_user.get("sub")
    current_user_organization_id = current_user.get("user_metadata", {}).get("organization_id")

    try:
        log.info(f"Creating customer_set with name: '{name}'")
        if organization_id != current_user_organization_id:
            raise BadRequestException(
                f"User does not belong to organization with id: '{organization_id}'"
            )

        try:
            await OrganizationRepository(db).get(id=organization_id)
            log.info(f"Organization with id: '{organization_id}' exists")
        except RecordNotFoundException:
            raise NotFoundException("Organization not found")

        data = CustomerSetDBInputSchema(
            name=name,
            description=description,
            organization_id=organization_id,
            type=type,
            status=CustomerSetStatus.UPLOADED.value,
            updated_by=current_user_id,
            created_by=current_user_id,
        )

        customer_set = await CustomerSetRepository(db).create(data)

        if file.size > 0:
            if file.content_type != "text/csv":
                raise BadRequestException(detail="Only CSV files are allowed")

            file_extension = file.filename.split(".")[-1]
            path = f"{customer_set.id}.{file_extension}"
            response = await supabase.storage.from_(SUPABASE_CUSTOMER_SET_BUCKET_NAME).upload(
                file=file.file.read(),
                path=path,
                file_options={"content-type": file.content_type},
            )
            log.debug(response.json())

            customer_set = await CustomerSetRepository(db).update(
                values={"url": path},
                id=customer_set.id,
            )

            process_csv_file_task.apply_async((customer_set.id,))
        return CustomerSetResponse(**customer_set.dict())
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("", response_model=List[CustomerSetResponse])
async def list_customer_sets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        log.info("Listing customer_sets")
        items = await CustomerSetRepository(db).list()
        return [CustomerSetResponse(**item.dict()) for item in items]
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.get("/{customer_set_id}", response_model=CustomerSetResponse)
async def get_customer_set(
    customer_set_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Getting customer_set for customer_set_id: '{customer_set_id}'")
        item = await CustomerSetRepository(db).get(id=customer_set_id)
        return CustomerSetResponse(**item.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.post("/{customer_set_id}/process", response_model=ProcessCustomerSetResponse)
async def process_customer_set(
    customer_set_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        log.info(f"Queuing processing for customer_set for customer_set_id: '{customer_set_id}'")
        item = await CustomerSetRepository(db).get(id=customer_set_id)
        # if item.status == CustomerSetStatus.PROCESSED.value:
        #     raise BadRequestException(detail="Customer set has already been processed")

        process_csv_file_task.apply_async((customer_set_id,))
        return ProcessCustomerSetResponse(message="Processing queued successfully")
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.patch("/{customer_set_id}", response_model=CustomerSetResponse)
async def update_customer_set(
    customer_set_id: str,
    payload: UpdateCustomerSetRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user_id = current_user.get("sub")
    try:
        log.info(f"Updating customer_set for customer_set_id: '{customer_set_id}'")
        customer_set = await CustomerSetRepository(db).update(
            values={**{**payload.dict(exclude_none=True), "updated_by": current_user_id}},
            id=customer_set_id,
        )
        return CustomerSetResponse(**customer_set.dict())
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)


@router.delete("/{customer_set_id}", status_code=204)
async def delete_customer_set(
    customer_set_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    supabase: SupabaseClient = Depends(get_supabase),
):
    try:
        customer_set = await CustomerSetRepository(db).get(id=customer_set_id)
        log.info(f"Deleting files for customer_set_id: '{customer_set_id}'")
        response = await supabase.storage.from_(SUPABASE_CUSTOMER_SET_BUCKET_NAME).remove(
            customer_set.url
        )
        log.debug(response)
        log.info(f"Deleting customer_set for customer_set_id: '{customer_set_id}'")
        await CustomerSetRepository(db).delete(id=customer_set_id)
    except RecordNotFoundException as e:
        raise NotFoundException(e)
    except ApplicationException as e:
        raise e
    except Exception as e:
        raise InternalServerException(e)
