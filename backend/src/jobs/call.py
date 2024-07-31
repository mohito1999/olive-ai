import os
from datetime import datetime, timedelta
from typing import Optional

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession
from vocode.streaming.models.agent import (
    AzureOpenAIConfig,
    ChatGPTAgentConfig,
    GroqAgentConfig,
    LangchainAgentConfig,
)
from vocode.streaming.models.client_backend import OutputAudioConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import (
    ElevenLabsSynthesizerConfig,
    GoogleSynthesizerConfig,
)
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
)
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramEndpointingConfig

from celeryworker import celery_app
from config import (
    BASE_URL,
    CALL_RETRY_INTERVAL,
    CALL_TIMEOUT_DURATION,
    CALL_TIMEOUT_TASK_INTERVAL,
    CHANNELS_AVAILABLE_COUNT,
    EXOTEL_ACCOUNT_SID,
    EXOTEL_API_KEY,
    EXOTEL_API_TOKEN,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)
from constants import (
    AgentConfigClass,
    CallStatus,
    CallType,
    CampaignStatus,
    SynthesizerConfigClass,
    TelephonyServiceConfigClass,
    TranscriberConfigClass,
)
from exceptions import RecordNotFoundException
from log import log
from models import Call, Customer, get_db
from repositories import (
    AgentRepository,
    CallRepository,
    CampaignRepository,
    CustomerRepository,
    OrganizationRepository,
    SynthesizerRepository,
    TelephonyServiceRepository,
    TranscriberRepository,
)
from schemas import CallDBInputSchema
from streaming.models.telephony import ExotelConfig
from streaming.telephony.conversation.outbound_call import CustomOutboundCall
from util.asyncio import async_to_sync
from util.config_manager import CONFIG_MANAGER


@celery_app.task(name="execute_campaign_task", bind=True)
def execute_campaign_task(self, campaign_id: str, customer_id: Optional[str] = None):
    async_to_sync(execute_campaign, campaign_id, customer_id)


async def execute_campaign(campaign_id: str, customer_id: Optional[str] = None):
    log.info(f"Executing campaign_id: {campaign_id}")

    db_gen = get_db()
    db: AsyncSession = await db_gen.__anext__()

    campaign = await CampaignRepository(db).get(id=campaign_id)
    if campaign.status != CampaignStatus.RUNNING.value:
        log.error(
            f"Skipping executing campaign_id: {campaign_id}. Status: {campaign.status} instead of RUNNING."
        )
        return
    current_user_id = campaign.updated_by
    organization = await OrganizationRepository(db).get(id=campaign.organization_id)
    customers = []

    if customer_id:
        customer = await CustomerRepository(db).get(id=customer_id)
        customers.append(customer)
    else:
        customers = await CustomerRepository(db).list(
            where=[
                Customer.organization_id == campaign.organization_id,
                Customer.customer_set_id.in_([set.id for set in campaign.customer_sets]),
            ]
        )

    if len(customers) == 0:
        log.error(f"No customers found to execute campaign_id: {campaign_id}")
        return
    log.info(f"Executing campaign_id: {campaign_id} for {len(customers)} customers")

    telephony_service_id = organization.telephony_service_id
    telephony_service_config = organization.telephony_service_config or {}
    agent_id = organization.agent_id
    agent_config = organization.agent_config or {}
    transcriber_id = organization.transcriber_id
    transcriber_config = organization.transcriber_config or {}
    synthesizer_id = organization.synthesizer_id
    synthesizer_config = organization.synthesizer_config or {}

    if campaign.telephony_service_id:
        telephony_service_id = campaign.telephony_service_id
        telephony_service_config = campaign.telephony_service_config or {}

    if campaign.agent_id:
        agent_id = campaign.agent_id
        agent_config = campaign.agent_config or {}

    if campaign.transcriber_id:
        transcriber_id = campaign.transcriber_id
        transcriber_config = campaign.transcriber_config or {}

    if campaign.synthesizer_id:
        synthesizer_id = campaign.synthesizer_id
        synthesizer_config = campaign.synthesizer_config or {}

    telephony_service = await TelephonyServiceRepository(db).get(id=telephony_service_id)
    agent = await AgentRepository(db).get(id=agent_id)
    transcriber = await TranscriberRepository(db).get(id=transcriber_id)
    synthesizer = await SynthesizerRepository(db).get(id=synthesizer_id)

    telephony_service_config = {**telephony_service.config, **telephony_service_config}
    agent_config = {**agent.config, **agent_config}
    transcriber_config = {**transcriber.config, **transcriber_config}
    synthesizer_config = {**synthesizer.config, **synthesizer_config}

    outbound_caller_number = telephony_service_config.pop("outbound_caller_number")

    # TODO: Optimize this with bulk_create
    for customer in customers:
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


class BaseTaskWithRetry(Task):
    max_retries = None


@celery_app.task(name="make_outbound_call_task", bind=True, base=BaseTaskWithRetry)
def make_outbound_call_task(self, call_id: str):
    async_to_sync(make_outbound_call, self, call_id)


async def make_outbound_call(self, call_id: str):
    log.info(f"Making outbound call for call_id: {call_id}")

    db_gen = get_db()
    db: AsyncSession = await db_gen.__anext__()

    call = await CallRepository(db).get(id=call_id)
    if call.status != CallStatus.PENDING.value:
        log.error(
            f"Skipping making outbound call for call_id: {call_id}. Status: {call.status} instead of PENDING."
        )
        return

    ongoing_calls_count = await CallRepository(db).count(
        where=[Call.status.in_([CallStatus.INITIATED.value, CallStatus.IN_PROGRESS.value])]
    )
    if ongoing_calls_count >= CHANNELS_AVAILABLE_COUNT:
        log.error("Can't make outbound call. Not enough channels available. Scheduled for retry.")
        raise self.retry(countdown=CALL_RETRY_INTERVAL)

    campaign = await CampaignRepository(db).get(id=call.campaign_id)
    customer = await CustomerRepository(db).get(id=call.customer_id)

    telephony_service_config_vocode = None
    agent_config_vocode = None
    transcriber_config_vocode = None
    synthesizer_config_vocode = None

    telephony_service_config_class = call.telephony_service_config.pop("config_class")
    agent_config_class = call.agent_config.pop("config_class")
    transcriber_config_class = call.transcriber_config.pop("config_class")
    synthesizer_config_class = call.synthesizer_config.pop("config_class")
    conversation_id = call.id
    telephony_params = None
    to_number = call.to_number
    prompt_variables = {
        "name": customer.name,
        "mobile_number": customer.mobile_number,
        **customer.customer_metadata,
    }
    prompt = campaign.prompt.format(**prompt_variables)
    initial_message = campaign.initial_message.format(**prompt_variables)

    if telephony_service_config_class == TelephonyServiceConfigClass.TWILIO.value:
        telephony_service_config_vocode = TwilioConfig(
            account_sid=TWILIO_ACCOUNT_SID,
            auth_token=TWILIO_AUTH_TOKEN,
            **call.telephony_service_config,
        )
        to_number = f"+91{to_number}"
    elif telephony_service_config_class == TelephonyServiceConfigClass.EXOTEL.value:
        telephony_service_config_vocode = ExotelConfig(
            account_sid=EXOTEL_ACCOUNT_SID,
            api_key=EXOTEL_API_KEY,
            api_token=EXOTEL_API_TOKEN,
            **call.telephony_service_config,
        )
        telephony_params = {
            "CustomField": conversation_id,
        }
        to_number = f"0{to_number}"

    if agent_config_class == AgentConfigClass.CHATGPT.value:
        azure_params = call.agent_config.pop("azure_params")
        if azure_params:
            agent_config_vocode = ChatGPTAgentConfig(
                **call.agent_config,
                prompt_preamble=prompt,
                initial_message=BaseMessage(text=initial_message),
                azure_params=AzureOpenAIConfig(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    **azure_params,
                ),
            )
        else:
            agent_config_vocode = ChatGPTAgentConfig(**call.agent_config)
    elif agent_config_class == AgentConfigClass.GROQ.value:
        agent_config_vocode = GroqAgentConfig(**call.agent_config)
    elif agent_config_class == AgentConfigClass.LANGCHAIN.value:
        agent_config_vocode = LangchainAgentConfig(**call.agent_config)

    if transcriber_config_class == TranscriberConfigClass.DEEPGRAM.value:
        endpointing_config = call.transcriber_config.pop("endpointing_config")
        if endpointing_config:
            transcriber_config_vocode = DeepgramTranscriberConfig(
                **call.transcriber_config,
                endpointing_config=DeepgramEndpointingConfig(**endpointing_config),
            )
        else:
            transcriber_config_vocode = DeepgramTranscriberConfig(**call.transcriber_config)

    if synthesizer_config_class == SynthesizerConfigClass.GOOGLE.value:
        output_audio_config = call.synthesizer_config.pop("output_audio_config")
        if output_audio_config:
            synthesizer_config_vocode = GoogleSynthesizerConfig.from_output_audio_config(
                **call.synthesizer_config,
                output_audio_config=OutputAudioConfig(**output_audio_config),
            )
        else:
            synthesizer_config_vocode = GoogleSynthesizerConfig.from_telephone_output_device(
                **call.synthesizer_config
            )
    elif synthesizer_config_class == SynthesizerConfigClass.ELEVEN_LABS.value:
        output_audio_config = call.synthesizer_config.pop("output_audio_config")
        if output_audio_config:
            synthesizer_config_vocode = ElevenLabsSynthesizerConfig.from_output_audio_config(
                api_key=os.getenv("ELEVEN_LABS_API_KEY"),
                **call.synthesizer_config,
                output_audio_config=OutputAudioConfig(**output_audio_config),
            )
        else:
            synthesizer_config_vocode = ElevenLabsSynthesizerConfig(
                api_key=os.getenv("ELEVEN_LABS_API_KEY"), **call.synthesizer_config
            )

    # log.debug(f"Telephony Service Config: {telephony_service_config_vocode}")
    # log.debug(f"Agent Config: {agent_config_vocode}")
    # log.debug(f"Transcriber Config: {transcriber_config_vocode}")
    # log.debug(f"Synthesizer Config: {synthesizer_config_vocode}")

    log.info(f"Initiating outbound call to '{to_number}'")
    init_succeeded = True
    try:
        outbound_call = CustomOutboundCall(
            base_url=BASE_URL,
            to_phone=to_number,
            from_phone=call.from_number,
            config_manager=CONFIG_MANAGER,
            conversation_id=conversation_id,
            transcriber_config=transcriber_config_vocode,
            agent_config=agent_config_vocode,
            synthesizer_config=synthesizer_config_vocode,
            telephony_config=telephony_service_config_vocode,
            telephony_params=telephony_params,
        )
        await outbound_call.start()
    except Exception as e:
        log.error(f"Error initiating outbound call: {e}")
        init_succeeded = False

    if init_succeeded:
        call.status = CallStatus.INITIATED.value
    else:
        call.status = CallStatus.FAILED.value
    await CallRepository(db).update(call, id=call.id)


@celery_app.task(name="timeout_initiated_calls_task")
def timeout_initiated_calls_task():
    async_to_sync(timeout_initiated_calls)


async def timeout_initiated_calls():
    db_gen = get_db()
    db: AsyncSession = await db_gen.__anext__()

    older_timestamp = datetime.utcnow() - timedelta(seconds=CALL_TIMEOUT_DURATION)
    try:
        await CallRepository(db).update(
            values={"status": CallStatus.TIMEOUT.value},
            where=[Call.updated_at <= older_timestamp, Call.status == CallStatus.INITIATED.value],
        )
    except RecordNotFoundException:
        pass


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    log.info(f"Registering periodic tasks on {sender}")
    sender.add_periodic_task(CALL_TIMEOUT_TASK_INTERVAL, timeout_initiated_calls_task)
    log.info(f"Registered periodic tasks on {sender}")
