import csv
from io import StringIO

from sqlalchemy.ext.asyncio import AsyncSession
from supabase._async.client import AsyncClient as SupabaseClient

from auth import get_supabase
from celeryworker import celery_app
from config import SUPABASE_CUSTOMER_SET_BUCKET_NAME
from constants import CustomerSetStatus
from log import log
from models import get_db
from repositories import CustomerRepository, CustomerSetRepository
from schemas import CustomerDBInputSchema
from util.asyncio import async_to_sync


@celery_app.task(name="process_csv_file")
def process_csv_file_task(customer_set_id: str):
    async_to_sync(process_csv_file, customer_set_id)


async def process_csv_file(customer_set_id: str):
    log.info(f"Processing CSV file for customer_set_id: {customer_set_id}")

    db_gen = get_db()
    db: AsyncSession = await db_gen.__anext__()

    supabase: SupabaseClient = await get_supabase()
    created_by = "system"

    customer_set = await CustomerSetRepository(db).get(id=customer_set_id)

    file = await supabase.storage.from_(SUPABASE_CUSTOMER_SET_BUCKET_NAME).download(
        customer_set.url
    )

    content = file.decode()
    str_content = StringIO(content)
    csv_file = csv.DictReader(str_content)

    deduped_customers = {}
    for row in csv_file:
        mobile_number = row.get("mobile_number")
        if mobile_number in deduped_customers:
            deduped_customers[mobile_number] = {**deduped_customers[mobile_number], **row}
        else:
            deduped_customers[mobile_number] = row

    customers = []
    for row in deduped_customers.values():
        name = row.pop("name")
        mobile_number = row.pop("mobile_number")
        metadata = row
        customer = CustomerDBInputSchema(
            organization_id=customer_set.organization_id,
            customer_set_id=customer_set.id,
            name=name,
            mobile_number=mobile_number,
            customer_metadata=metadata,
            created_by=created_by,
            updated_by=created_by,
        )
        customers.append(customer)

    await CustomerRepository(db).bulk_create(
        customers,
        on_conflict=lambda q: {"constraint": "customer_set_id_mobile_number_uc"},
    )

    customer_set.status = CustomerSetStatus.PROCESSED
    await CustomerSetRepository(db).update(customer_set, id=customer_set.id)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    log.info(f"Registering periodic tasks on {sender}")
    # Periodic tasks
    log.info(f"Registered periodic tasks on {sender}")
