import logging
import os
from typing import Optional

import sentry_sdk
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from src.custom_agent import LogToConsoleActionConfig
from src.custom_telephony_server import CustomTelephonyServer
from src.streaming.models.telephony import ExotelConfig
from src.streaming.telephony.constants import EXOTEL_AUDIO_ENCODING, EXOTEL_CHUNK_SIZE
from src.streaming.telephony.conversation.outbound_call import CustomOutboundCall
from src.streaming.telephony.server.base import ExotelInboundCallConfig
from vocode.logging import configure_json_logging, configure_pretty_logging
from vocode.streaming.models.agent import (
    AnthropicAgentConfig,
    AzureOpenAIConfig,
    ChatGPTAgentConfig,
    GroqAgentConfig,
    InterruptSensitivity,
    LangchainAgentConfig,
)
from vocode.streaming.models.client_backend import OutputAudioConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import GoogleSynthesizerConfig
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.transcriber import (
    DEFAULT_AUDIO_ENCODING,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_SAMPLING_RATE,
    DeepgramTranscriberConfig,
)
from vocode.streaming.telephony.config_manager.in_memory_config_manager import (
    InMemoryConfigManager,
)
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramEndpointingConfig
from vocode.streaming.utils import create_conversation_id

# DO NOT REMOVE
import llama_monkey_patch

DEPLOYED_ENVIRONMENTS = ["production", "staging"]
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


def configure_logging() -> None:  # pragma: no cover
    """Configures logging."""
    if ENVIRONMENT in DEPLOYED_ENVIRONMENTS:
        configure_json_logging()
    else:
        configure_pretty_logging()


configure_logging()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=ENVIRONMENT,
    integrations=[
        AsyncioIntegration(),
        LoguruIntegration(),
    ],
)

app = FastAPI(docs_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

TWILIO_CONFIG = TwilioConfig(
    account_sid=os.getenv("TWILIO_ACCOUNT_SID") or "<your twilio account sid>",
    auth_token=os.getenv("TWILIO_AUTH_TOKEN") or "<your twilio auth token>",
)
EXOTEL_CONFIG = ExotelConfig(
    account_sid=os.environ["EXOTEL_ACCOUNT_SID"],
    api_key=os.environ["EXOTEL_API_KEY"],
    api_token=os.environ["EXOTEL_API_TOKEN"],
    app_id=os.environ["EXOTEL_APP_ID"],
    subdomain="api.exotel.com",
)

OUTBOUND_CALLER_NUMBER = os.getenv("OUTBOUND_CALLER_NUMBER")

CONFIG_MANAGER = InMemoryConfigManager()  # RedisConfigManager()

# SYNTH_CONFIG = StreamElementsSynthesizerConfig.from_telephone_output_device()
# SYNTH_CONFIG = ElevenLabsSynthesizerConfig.from_telephone_output_device(
#   api_key=os.getenv("ELEVEN_LABS_API_KEY") or "<your EL token>",
#   voice_id="zT03pEAEi0VHKciJODfn"
# )
# SYNTH_CONFIG = GoogleSynthesizerConfig.from_telephone_output_device(language_code="en-IN", voice_name="en-IN-Wavenet-B", pitch=-5.0)
# SYNTH_CONFIG = AzureSynthesizerConfig.from_telephone_output_device(
#     language="en-IN",
#     voice_name="en-IN-AashiNeural",
#     rate=25,
# )
# SYNTH_CONFIG = PlayHtSynthesizerConfig.from_telephone_output_device(voce_id="")

TRANSCRIBER_CONFIG = DeepgramTranscriberConfig(
    language="hi",
    model="nova-2",
    sampling_rate=DEFAULT_SAMPLING_RATE.value,
    audio_encoding=DEFAULT_AUDIO_ENCODING,
    chunk_size=DEFAULT_CHUNK_SIZE,
    endpointing_config=DeepgramEndpointingConfig(),
)


DEFAULT_INITIAL_MESSAGE = "Hello, am I speaking to Mohit?"
DEFAULT_PROMPT = """You can Kunal from Apple. You are free to call the tools provided to you. NEVER say anything else when calling a tool, not even things like 'Please call the following tool'. You can talk in English or Hindi. 
Goal: Help recover sales drop-offs and abandoned carts for customers by engaging in conversation and understanding their needs. This how I want the call flow to look like: 
Start by Introducing yourself as Kunal and say you are calling from Apple. Verify that you are speaking with the customer by using their Mohit wherever applicable. Then you Identify the Issue and Inform the customer that you noticed they did not go through with the process for purchasing iPhone 15. Ask if there is any assistance needed and wait for their response.
As per their response, respond accordingly: If the customer cites pricing or commercials as an issue, offer something to resolve that makes sense.
If the customer is unsure about the process or something else, provide clarification and assistance as needed.
Do make Industry-Specific Adjustments:
Adjust your call according to the industry you are representing. For example:
If you are an agent from Rebook and the iPhone 15 is a pair of shoes, tailor your call to fit that context.
If you are an agent from Volt Money and the iPhone 15 is a personal loan, use appropriate lingo and style.
End with a Conclusion where you Thank the customer for their time and provide contact information if they need to get in touch.
"""
DEFAULT_VOICE = "hi-IN-Wavenet-B"


# Let's create and expose that TelephonyServer.
telephony_server = CustomTelephonyServer(
    base_url=BASE_URL,
    config_manager=CONFIG_MANAGER,
    inbound_call_configs=[
        ExotelInboundCallConfig(
            url="/inbound_exotel",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text=DEFAULT_INITIAL_MESSAGE),
                prompt_preamble=DEFAULT_PROMPT,
            ),
            exotel_config=EXOTEL_CONFIG,
        )
    ],
)
app.include_router(telephony_server.get_router())


class OutboundCallRequest(BaseModel):
    mobile_number: str
    name: str
    company: str
    company_product: str
    prompt: Optional[str] = DEFAULT_PROMPT
    initial_message: Optional[str] = DEFAULT_INITIAL_MESSAGE
    interrupt_sensitivity: Optional[InterruptSensitivity] = "low"
    voice: Optional[str] = DEFAULT_VOICE


@app.post("/start_outbound_call")
async def api_start_outbound_call(
    req: OutboundCallRequest, api_key: str = Header(alias="x-api-key")
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    mobile_number = req.mobile_number
    name = req.name
    company = req.company
    company_product = req.company_product
    interrupt_sensitivity = req.interrupt_sensitivity
    voice = req.voice or DEFAULT_VOICE

    prompt_variables = {
        "name": name,
        "company": company,
        "company_product": company_product,
    }
    prompt = req.prompt.format(**prompt_variables)
    initial_message = req.initial_message.format(**prompt_variables)
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Initial Message: {initial_message}")
    logger.info(f"Interrupt Sensitivity: {interrupt_sensitivity}")
    logger.info(f"Voice: {voice}")

    transcriber_config = DeepgramTranscriberConfig(
        language="hi",
        model="nova-2",
        sampling_rate=DEFAULT_SAMPLING_RATE.value,
        audio_encoding=EXOTEL_AUDIO_ENCODING,
        chunk_size=EXOTEL_CHUNK_SIZE,
        endpointing_config=DeepgramEndpointingConfig(),
    )
    synth_config = GoogleSynthesizerConfig.from_output_audio_config(
        output_audio_config=OutputAudioConfig(
            sampling_rate=DEFAULT_SAMPLING_RATE.value,
            audio_encoding=EXOTEL_AUDIO_ENCODING,
        ),
        language_code="hi-IN",
        voice_name=voice,
        pitch=-10.0,
    )
    # synth_config = CartesiaSynthesizerConfig.from_telephone_output_device(
    #     model_id="sonic-english",
    #     voice_id="638efaaa-4d0c-442e-b701-3fae16aad012",
    # )

    # agent_config = GroqAgentConfig(
    #     model_name="llama3-8b-8192",
    #     initial_message=BaseMessage(text=initial_message),
    #     prompt_preamble=prompt,
    #     temperature=0.5,
    #     interrupt_sensitivity=interrupt_sensitivity,
    #     actions=[LogToConsoleActionConfig(type="action_log_message_to_console")],
    # )

    # agent_config = LangchainAgentConfig(
    #     model_name="llama3-70b-8192",
    #     # model_name="mistral.mistral-7b-instruct-v0:2",
    #     # model_name="mistral.mixtral-8x7b-instruct-v0:1",
    #     # model_name="meta.llama3-8b-instruct-v1:0",
    #     provider="groq",
    #     initial_message=BaseMessage(text=initial_message),
    #     prompt_preamble=prompt,
    #     temperature=0.5,
    #     interrupt_sensitivity=interrupt_sensitivity,
    # )
    # agent_config = LangchainAgentConfig(
    #     model_name="gemini-1.5-flash-001",
    #     provider="google_vertexai",
    #     # provider="google_genai",
    #     initial_message=BaseMessage(text=initial_message),
    #     prompt_preamble=prompt,
    #     temperature=1,
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
        )
    )
    # agent_config = ChatVertexAIAgentConfig(
    #     model_name="gemini-1.5-flash-001",
    #     initial_message=BaseMessage(text=initial_message),
    #     prompt_preamble=prompt,
    #     interrupt_sensitivity=interrupt_sensitivity,
    #     actions=[LogToConsoleActionConfig(type="action_log_message_to_console")],
    # )

    conversation_id = create_conversation_id()
    telephony_params = {
        "CustomField": conversation_id,
    }
    logger.info(f"Conversation ID: {conversation_id}")

    logger.info(f"Starting outbound call to {mobile_number}")
    outbound_call = CustomOutboundCall(
        base_url=BASE_URL,
        to_phone=mobile_number,
        from_phone=OUTBOUND_CALLER_NUMBER,
        config_manager=CONFIG_MANAGER,
        transcriber_config=transcriber_config,
        agent_config=agent_config,
        synthesizer_config=synth_config,
        telephony_config=EXOTEL_CONFIG,
        telephony_params=telephony_params,
        conversation_id=conversation_id,
    )
    await outbound_call.start()
    return {"status": "success"}


uvicorn.run(app, host="0.0.0.0", port=3000)
