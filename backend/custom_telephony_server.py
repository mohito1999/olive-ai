from typing import List, Optional

from fastapi import APIRouter, Form, Request, Response, Query
from loguru import logger

from vocode.streaming.agent.abstract_factory import AbstractAgentFactory
from vocode.streaming.agent.default_factory import DefaultAgentFactory
from vocode.streaming.models.telephony import (
    TwilioCallConfig,
    VonageCallConfig,
)

from vocode.streaming.synthesizer.abstract_factory import AbstractSynthesizerFactory
from vocode.streaming.synthesizer.default_factory import DefaultSynthesizerFactory
from vocode.streaming.telephony.config_manager.base_config_manager import (
    BaseConfigManager,
)
from vocode.streaming.telephony.server.router.calls import CallsRouter
from vocode.streaming.transcriber.abstract_factory import AbstractTranscriberFactory
from vocode.streaming.transcriber.default_factory import DefaultTranscriberFactory
from vocode.streaming.utils.events_manager import EventsManager
from vocode.streaming.telephony.server.base import TelephonyServer, AbstractInboundCallConfig


from vocode.streaming.models.telephony import BaseCallConfig
from vocode.streaming.telephony.conversation.abstract_phone_conversation import (
    AbstractPhoneConversation,
)
from vocode.streaming.telephony.conversation.twilio_phone_conversation import (
    TwilioPhoneConversation,
)
from vocode.streaming.telephony.conversation.vonage_phone_conversation import (
    VonagePhoneConversation,
)

from functools import partial
from vocode.streaming.models.telephony import (
    TwilioConfig,
    VonageConfig,
)
from vocode.streaming.telephony.client.vonage_client import VonageClient
from vocode.streaming.telephony.server.base import TwilioInboundCallConfig, VonageInboundCallConfig, VonageAnswerRequest
from vocode.streaming.telephony.templater import get_connection_twiml
from vocode.streaming.utils import create_conversation_id

from streaming.telephony.conversation.exotel_phone_conversation import ExotelPhoneConversation
from streaming.telephony.server.base import ExotelInboundCallConfig
from streaming.telephony.client.exotel_client import ExotelClient
from streaming.models.telephony import ExotelCallConfig, ExotelConfig

from custom_agent import CustomAgentFactory
from custom_synth import CustomSynthesizerFactory


class CustomCallsRouter(CallsRouter):
    def _from_call_config(
        self,
        base_url: str,
        call_config: BaseCallConfig,
        config_manager: BaseConfigManager,
        conversation_id: str,
        transcriber_factory: AbstractTranscriberFactory = DefaultTranscriberFactory(),
        agent_factory: AbstractAgentFactory = DefaultAgentFactory(),
        synthesizer_factory: AbstractSynthesizerFactory = DefaultSynthesizerFactory(),
        events_manager: Optional[EventsManager] = None,
    ) -> AbstractPhoneConversation:
        if isinstance(call_config, TwilioCallConfig):
            return TwilioPhoneConversation(
                to_phone=call_config.to_phone,
                from_phone=call_config.from_phone,
                base_url=base_url,
                config_manager=config_manager,
                agent_config=call_config.agent_config,
                transcriber_config=call_config.transcriber_config,
                synthesizer_config=call_config.synthesizer_config,
                twilio_config=call_config.twilio_config,
                twilio_sid=call_config.twilio_sid,
                conversation_id=conversation_id,
                transcriber_factory=transcriber_factory,
                agent_factory=agent_factory,
                synthesizer_factory=synthesizer_factory,
                events_manager=events_manager,
                direction=call_config.direction,
                speed_coefficient=2.0
            )
        elif isinstance(call_config, VonageCallConfig):
            return VonagePhoneConversation(
                to_phone=call_config.to_phone,
                from_phone=call_config.from_phone,
                base_url=base_url,
                config_manager=config_manager,
                agent_config=call_config.agent_config,
                transcriber_config=call_config.transcriber_config,
                synthesizer_config=call_config.synthesizer_config,
                vonage_config=call_config.vonage_config,
                vonage_uuid=call_config.vonage_uuid,
                conversation_id=conversation_id,
                transcriber_factory=transcriber_factory,
                agent_factory=agent_factory,
                synthesizer_factory=synthesizer_factory,
                events_manager=events_manager,
                output_to_speaker=call_config.output_to_speaker,
                direction=call_config.direction,
                speed_coefficient=2.0
            )
        elif isinstance(call_config, ExotelCallConfig):
            return ExotelPhoneConversation(
                to_phone=call_config.to_phone,
                from_phone=call_config.from_phone,
                base_url=base_url,
                config_manager=config_manager,
                agent_config=call_config.agent_config,
                transcriber_config=call_config.transcriber_config,
                synthesizer_config=call_config.synthesizer_config,
                vonage_config=call_config.vonage_config,
                vonage_uuid=call_config.vonage_uuid,
                conversation_id=conversation_id,
                transcriber_factory=transcriber_factory,
                agent_factory=agent_factory,
                synthesizer_factory=synthesizer_factory,
                events_manager=events_manager,
                output_to_speaker=call_config.output_to_speaker,
                direction=call_config.direction,
                speed_coefficient=2.0
            )
        else:
            raise ValueError(f"Unknown call config type {call_config.type}")


class CustomTelephonyServer(TelephonyServer):
    def __init__(
        self,
        base_url: str,
        config_manager: BaseConfigManager,
        inbound_call_configs: List[AbstractInboundCallConfig] = [],
        transcriber_factory: AbstractTranscriberFactory = DefaultTranscriberFactory(),
        agent_factory: AbstractAgentFactory = CustomAgentFactory(),
        synthesizer_factory: AbstractSynthesizerFactory = CustomSynthesizerFactory(),
        events_manager: Optional[EventsManager] = None,
    ):
        self.base_url = base_url
        self.router = APIRouter()
        self.config_manager = config_manager
        self.events_manager = events_manager
        self.router.include_router(
            CustomCallsRouter(
                base_url=base_url,
                config_manager=self.config_manager,
                transcriber_factory=transcriber_factory,
                agent_factory=agent_factory,
                synthesizer_factory=synthesizer_factory,
                events_manager=self.events_manager,
            ).get_router()
        )
        for config in inbound_call_configs:
            self.router.add_api_route(
                config.url,
                self.create_inbound_route(inbound_call_config=config),
                methods=["POST"],
            )
        # vonage requires an events endpoint
        self.router.add_api_route("/events", self.events, methods=["GET", "POST"])
        logger.info(f"Set up events endpoint at https://{self.base_url}/events")

        self.router.add_api_route(
            "/recordings/{conversation_id}", self.recordings, methods=["GET", "POST"]
        )
        logger.info(
            f"Set up recordings endpoint at https://{self.base_url}/recordings/{{conversation_id}}"
        )

    def create_inbound_route(
        self,
        inbound_call_config: AbstractInboundCallConfig,
    ):
        async def twilio_route(
            twilio_config: TwilioConfig,
            twilio_sid: str = Form(alias="CallSid"),
            twilio_from: str = Form(alias="From"),
            twilio_to: str = Form(alias="To"),
        ) -> Response:
            call_config = TwilioCallConfig(
                transcriber_config=inbound_call_config.transcriber_config
                or TwilioCallConfig.default_transcriber_config(),
                agent_config=inbound_call_config.agent_config,
                synthesizer_config=inbound_call_config.synthesizer_config
                or TwilioCallConfig.default_synthesizer_config(),
                twilio_config=twilio_config,
                twilio_sid=twilio_sid,
                from_phone=twilio_from,
                to_phone=twilio_to,
                direction="inbound",
            )

            conversation_id = create_conversation_id()
            await self.config_manager.save_config(conversation_id, call_config)
            return get_connection_twiml(base_url=self.base_url, call_id=conversation_id)

        async def exotel_route(
            # client_id: str,
            exotel_config: ExotelConfig,
            exotel_sid: str = Query(..., alias="CallSid"),
            exotel_from: str = Query(..., alias="CallFrom"),
            exotel_to: str = Query(..., alias="CallTo"),
        ):
            logger.info(f"Call connected from: {exotel_from}  --->  {exotel_to}")
            # client_specific_config = await self.config_manager.get_client_config(client_id)
            # if not isinstance(client_specific_config, ExotelClientConfig):
            #     await self.add_route_async(inbound_call_config)

            call_config = ExotelCallConfig(
                transcriber_config=inbound_call_config.transcriber_config
                or ExotelCallConfig.default_transcriber_config(),
                agent_config=inbound_call_config.agent_config,
                synthesizer_config=inbound_call_config.synthesizer_config
                or ExotelCallConfig.default_synthesizer_config(),
                exotel_config=exotel_config,
                exotel_sid=exotel_sid,
                from_phone=exotel_from,
                to_phone=exotel_to,
            )
            conversation_id = create_conversation_id()
            await self.config_manager.save_config(conversation_id, call_config)
            return ExotelClient.create_call_exotel(
                base_url=self.base_url,
                conversation_id=conversation_id,
            )
        
        async def exotel_route_new(
            exotel_config: ExotelConfig,
            # exotel_sid: str = Form(alias="CallSid"),
            request: Request,
        ) -> Response:
            logger.debug(f"Received Exotel call request: {await request.text()}")
            call_config = ExotelCallConfig(
                transcriber_config=inbound_call_config.transcriber_config
                or ExotelCallConfig.default_transcriber_config(),
                agent_config=inbound_call_config.agent_config,
                synthesizer_config=inbound_call_config.synthesizer_config
                or ExotelCallConfig.default_synthesizer_config(),
                exotel_config=exotel_config,
                # exotel_sid=exotel_sid,
                direction="inbound",
            )

            conversation_id = create_conversation_id()
            await self.config_manager.save_config(conversation_id, call_config)
            return get_connection_twiml(base_url=self.base_url, call_id=conversation_id)

        async def vonage_route(vonage_config: VonageConfig, request: Request):
            vonage_answer_request = VonageAnswerRequest.parse_obj(await request.json())
            call_config = VonageCallConfig(
                transcriber_config=inbound_call_config.transcriber_config
                or VonageCallConfig.default_transcriber_config(),
                agent_config=inbound_call_config.agent_config,
                synthesizer_config=inbound_call_config.synthesizer_config
                or VonageCallConfig.default_synthesizer_config(),
                vonage_config=vonage_config,
                vonage_uuid=vonage_answer_request.uuid,
                to_phone=vonage_answer_request.from_,
                from_phone=vonage_answer_request.to,
                direction="inbound",
            )
            conversation_id = create_conversation_id()
            await self.config_manager.save_config(conversation_id, call_config)
            vonage_client = VonageClient(
                base_url=self.base_url,
                maybe_vonage_config=vonage_config,
                record_calls=vonage_config.record,
            )
            return vonage_client.create_call_ncco(
                conversation_id=conversation_id,
                record=vonage_config.record,
            )

        if isinstance(inbound_call_config, TwilioInboundCallConfig):
            logger.info(
                f"Set up inbound call TwiML at https://{self.base_url}{inbound_call_config.url}"
            )
            return partial(twilio_route, inbound_call_config.twilio_config)
        elif isinstance(inbound_call_config, VonageInboundCallConfig):
            logger.info(
                f"Set up inbound call NCCO at https://{self.base_url}{inbound_call_config.url}"
            )
            return partial(vonage_route, inbound_call_config.vonage_config)
        elif isinstance(inbound_call_config, ExotelInboundCallConfig):
            logger.info(
                f"Set up inbound call Exotel at https://{self.base_url}{inbound_call_config.url}"
            )
            return partial(exotel_route, inbound_call_config.exotel_config)
        else:
            raise ValueError(f"Unknown inbound call config type {type(inbound_call_config)}")
