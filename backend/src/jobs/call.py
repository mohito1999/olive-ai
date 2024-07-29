import os

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
    CustomerSetStatus,
    SynthesizerConfigClass,
    TelephonyServiceConfigClass,
    TranscriberConfigClass,
)
from log import log
from models import get_db
from repositories import CallRepository, CampaignRepository, CustomerRepository
from streaming.models.telephony import ExotelConfig
from streaming.telephony.conversation.outbound_call import CustomOutboundCall
from util.asyncio import async_to_sync
from util.config_manager import CONFIG_MANAGER


@celery_app.task(name="make_outbound_call_task")
def make_outbound_call_task(call_id: str):
    async_to_sync(make_outbound_call, call_id)


async def make_outbound_call(call_id: str):
    log.info(f"Making outbound call for call_id: {call_id}")

    db_gen = get_db()
    db: AsyncSession = await db_gen.__anext__()

    call = await CallRepository(db).get(id=call_id)
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

    call.status = CallStatus.INITIATED.value
    call = await CallRepository(db).update(call, id=call.id)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    log.info(f"Registering periodic tasks on {sender}")
    # Periodic tasks
    log.info(f"Registered periodic tasks on {sender}")
