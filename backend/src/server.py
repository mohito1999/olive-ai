import sentry_sdk
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from vocode.streaming.models.agent import ChatGPTAgentConfig

import config

# DO NOT REMOVE
import llama_monkey_patch
from constants import DEFAULT_PROMPT
from custom_agent import LogToConsoleActionConfig
from custom_telephony_server import CustomTelephonyServer
from exceptions import add_exception_handlers
from log import log
from resources import (
    agent,
    auth,
    campaign,
    health,
    organization,
    outbound_call,
    synthesizer,
    telephony_service,
    transcriber,
)
from streaming.telephony.server.base import ExotelInboundCallConfig
from util.config_manager import CONFIG_MANAGER
from util.security_headers import add_security_headers
from util.telephony_server import EXOTEL_CONFIG

log.warning(" ██████╗ ██╗     ██╗██╗   ██╗███████╗")
log.warning("██╔═══██╗██║     ██║██║   ██║██╔════╝")
log.warning("██║   ██║██║     ██║██║   ██║█████╗  ")
log.warning("██║   ██║██║     ██║╚██╗ ██╔╝██╔══╝  ")
log.warning("╚██████╔╝███████╗██║ ╚████╔╝ ███████╗")
log.warning(" ╚═════╝ ╚══════╝╚═╝  ╚═══╝  ╚══════╝")

app = FastAPI(
    title="olive-ai",
    version="v1",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://app.oliveai.in",
        "https://olive-ai-git-next-js-mohit-motwanis-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Referer", "User-Agent"],
)
app.add_middleware(CorrelationIdMiddleware)
add_security_headers(app)
add_exception_handlers(app)


sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    environment=config.ENVIRONMENT,
    integrations=[
        AsyncioIntegration(),
        LoguruIntegration(),
    ],
)

telephony_server = CustomTelephonyServer(
    base_url=config.BASE_URL,
    config_manager=CONFIG_MANAGER,
    inbound_call_configs=[
        ExotelInboundCallConfig(
            url="/inbound_exotel",
            agent_config=ChatGPTAgentConfig(
                prompt_preamble=DEFAULT_PROMPT,
            ),
            exotel_config=EXOTEL_CONFIG,
        )
    ],
)
# app.include_router(telephony_server.get_router())

api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(organization.router, prefix="/organizations", tags=["organization"])
api_router.include_router(agent.router, prefix="/agents", tags=["agent"])
api_router.include_router(transcriber.router, prefix="/transcribers", tags=["transcriber"])
api_router.include_router(synthesizer.router, prefix="/synthesizers", tags=["synthesizer"])
api_router.include_router(telephony_service.router, prefix="/telephony-services", tags=["telephony_service"])
api_router.include_router(campaign.router, prefix="/campaigns", tags=["campaign"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(outbound_call.router, prefix="/calls", tags=["call"])
app.include_router(api_router)
