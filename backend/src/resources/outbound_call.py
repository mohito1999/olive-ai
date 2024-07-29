import os

from fastapi import APIRouter, Depends
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
from vocode.streaming.models.transcriber import (
    DEFAULT_AUDIO_ENCODING,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_SAMPLING_RATE,
    DeepgramTranscriberConfig,
)
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramEndpointingConfig
from vocode.streaming.utils import create_conversation_id

from auth import get_current_user
from config import BASE_URL, EXOTEL_OUTBOUND_CALLER_NUMBER, TWILIO_OUTBOUND_CALLER_NUMBER
from log import log
from models import get_db
from schemas import OutboundCallRequest
from streaming.telephony.constants import EXOTEL_AUDIO_ENCODING, EXOTEL_CHUNK_SIZE
from streaming.telephony.conversation.outbound_call import CustomOutboundCall
from util.config_manager import CONFIG_MANAGER
from util.telephony_server import EXOTEL_CONFIG, TWILIO_CONFIG

router = APIRouter()


@router.post("/outbound")
async def start_outbound_call(
    payload: OutboundCallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    mobile_number = payload.mobile_number
    name = payload.name
    company = payload.company
    company_product = payload.company_product
    interrupt_sensitivity = payload.interrupt_sensitivity
    voice = payload.voice

    prompt_variables = {
        "name": name,
        "company": company,
        "company_product": company_product,
    }
    prompt = payload.prompt.format(**prompt_variables)
    initial_message = payload.initial_message.format(**prompt_variables)
    log.info(f"Prompt: {prompt}")
    log.info(f"Initial Message: {initial_message}")
    log.info(f"Interrupt Sensitivity: {interrupt_sensitivity}")
    log.info(f"Voice: {voice}")

    transcriber_config = DeepgramTranscriberConfig(
        language="hi",
        model="nova-2",
        sampling_rate=DEFAULT_SAMPLING_RATE.value,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        chunk_size=DEFAULT_CHUNK_SIZE,
        # audio_encoding=EXOTEL_AUDIO_ENCODING,
        # chunk_size=EXOTEL_CHUNK_SIZE,
        endpointing_config=DeepgramEndpointingConfig(
            vad_threshold_ms=300, use_single_utterance_endpointing_for_first_utterance=True
        ),
    )
    if payload.synthesizer == "elevenlabs":
        synth_config = ElevenLabsSynthesizerConfig.from_telephone_output_device(
            api_key=os.getenv("ELEVEN_LABS_API_KEY"),
            voice_id=voice,
            model_id="eleven_turbo_v2_5",
            stability=1,
            # experimental_websocket=True,
            # experimental_streaming=True,
            optimize_streaming_latency=3,
            similarity_boost=0,
        )
    elif payload.synthesizer == "google":
        synth_config = GoogleSynthesizerConfig.from_output_audio_config(
            output_audio_config=OutputAudioConfig(
                sampling_rate=DEFAULT_SAMPLING_RATE.value,
                audio_encoding=DEFAULT_AUDIO_ENCODING,
                # audio_encoding=EXOTEL_AUDIO_ENCODING,
            ),
            language_code="hi-IN",
            voice_name=voice,
            pitch=-10.0,
            speaking_rate=1.1,
        )

    log.info(f"Synthesizer Config: {synth_config}")

    # agent_config = GroqAgentConfig(
    #     model_name="llama3-8b-8192",
    #     initial_message=BaseMessage(text=initial_message),
    #     prompt_preamble=prompt,
    #     temperature=0.5,
    #     interrupt_sensitivity=interrupt_sensitivity,
    #     end_conversation_on_goodbye=True,
    #     goodbye_phrases=["bye"],
    #     # actions=[LogToConsoleActionConfig(type="action_log_message_to_console")],
    # )
    # agent_config = LangchainAgentConfig(
    #     # model_name="llama3-70b-8192",
    #     # model_name="mistral.mistral-7b-instruct-v0:2",
    #     # model_name="mistral.mixtral-8x7b-instruct-v0:1",
    #     model_name="meta.llama3-8b-instruct-v1:0",
    #     provider="bedrock",
    #     initial_message=BaseMessage(text=initial_message),
    #     prompt_preamble=prompt,
    #     temperature=0.5,
    #     interrupt_sensitivity=interrupt_sensitivity,
    # )

    agent_config = ChatGPTAgentConfig(
        initial_message=BaseMessage(text=initial_message),
        prompt_preamble=prompt,
        temperature=0.5,
        interrupt_sensitivity=interrupt_sensitivity,
        # actions=[LogToConsoleActionConfig(type="action_log_message_to_console")],
        end_conversation_on_goodbye=True,
        goodbye_phrases=["bye"],
        azure_params=AzureOpenAIConfig(
            openai_model_name="gpt-35-turbo-0125",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            region="southindia",
            deployment_name="olive-ai",
            api_version="2024-06-01",
        ),
    )

    conversation_id = create_conversation_id()
    telephony_params = {
        "CustomField": conversation_id,
    }

    log.info(f"Starting outbound call to {mobile_number}")
    outbound_call = CustomOutboundCall(
        base_url=BASE_URL,
        to_phone=mobile_number,
        # from_phone=EXOTEL_OUTBOUND_CALLER_NUMBER,
        from_phone=TWILIO_OUTBOUND_CALLER_NUMBER,
        config_manager=CONFIG_MANAGER,
        transcriber_config=transcriber_config,
        agent_config=agent_config,
        synthesizer_config=synth_config,
        # telephony_config=EXOTEL_CONFIG,
        telephony_config=TWILIO_CONFIG,
        telephony_params=telephony_params,
        conversation_id=conversation_id,
    )
    await outbound_call.start()
    return {"status": "success"}
