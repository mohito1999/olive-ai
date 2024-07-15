from typing import Optional

from loguru import logger

from vocode.streaming.models.synthesizer import SynthesizerConfig
from vocode.streaming.models.telephony import (
    TwilioCallConfig,
    TwilioConfig,
    VonageCallConfig,
    VonageConfig,
)
from vocode.streaming.models.transcriber import TranscriberConfig
from vocode.streaming.telephony.client.abstract_telephony_client import AbstractTelephonyClient
from vocode.streaming.telephony.client.twilio_client import TwilioClient
from vocode.streaming.telephony.client.vonage_client import VonageClient
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall

from streaming.models.telephony import ExotelConfig, ExotelCallConfig
from streaming.telephony.client.exotel_client import ExotelClient


class CustomOutboundCall(OutboundCall):
    def create_telephony_client(self) -> AbstractTelephonyClient:
        if isinstance(self.telephony_config, TwilioConfig):
            return TwilioClient(base_url=self.base_url, maybe_twilio_config=self.telephony_config)
        elif isinstance(self.telephony_config, VonageConfig):
            return VonageClient(base_url=self.base_url, maybe_vonage_config=self.telephony_config)
        elif isinstance(self.telephony_config, ExotelConfig):
            return ExotelClient(base_url=self.base_url, maybe_exotel_config=self.telephony_config)

    def create_transcriber_config(
        self, transcriber_config_override: Optional[TranscriberConfig]
    ) -> TranscriberConfig:
        if transcriber_config_override is not None:
            return transcriber_config_override
        if isinstance(self.telephony_config, TwilioConfig):
            return TwilioCallConfig.default_transcriber_config()
        elif isinstance(self.telephony_config, VonageConfig):
            return VonageCallConfig.default_transcriber_config()
        elif isinstance(self.telephony_config, ExotelConfig):
            return ExotelCallConfig.default_transcriber_config()
        else:
            raise ValueError("No telephony config provided")

    def create_synthesizer_config(
        self, synthesizer_config_override: Optional[SynthesizerConfig]
    ) -> SynthesizerConfig:
        if synthesizer_config_override is not None:
            return synthesizer_config_override
        if isinstance(self.telephony_config, TwilioConfig):
            return TwilioCallConfig.default_synthesizer_config()
        elif isinstance(self.telephony_config, VonageConfig):
            return VonageCallConfig.default_synthesizer_config()
        elif isinstance(self.telephony_config, ExotelConfig):
            return ExotelCallConfig.default_synthesizer_config()
        else:
            raise ValueError("No telephony config provided")

    async def start(self):
        logger.debug("Starting outbound call")
        self.telephony_id = await self.telephony_client.create_call(
            conversation_id=self.conversation_id,
            to_phone=self.to_phone,
            from_phone=self.from_phone,
            record=self.telephony_client.get_telephony_config().record,  # note twilio does not use this
            telephony_params=self.telephony_params,
            digits=self.digits,
        )
        if isinstance(self.telephony_client, TwilioClient):
            call_config = TwilioCallConfig(
                transcriber_config=self.transcriber_config,
                agent_config=self.agent_config,
                synthesizer_config=self.synthesizer_config,
                twilio_config=self.telephony_client.twilio_config,
                twilio_sid=self.telephony_id,
                from_phone=self.from_phone,
                to_phone=self.to_phone,
                sentry_tags=self.sentry_tags,
                telephony_params=self.telephony_params,
                direction="outbound",
            )
        elif isinstance(self.telephony_client, VonageClient):
            call_config = VonageCallConfig(
                transcriber_config=self.transcriber_config,
                agent_config=self.agent_config,
                synthesizer_config=self.synthesizer_config,
                vonage_config=self.telephony_client.vonage_config,
                vonage_uuid=self.telephony_id,
                from_phone=self.from_phone,
                to_phone=self.to_phone,
                output_to_speaker=False,
                sentry_tags=self.sentry_tags,
                telephony_params=self.telephony_params,
                direction="outbound",
            )
        elif isinstance(self.telephony_client, ExotelClient):
            call_config = ExotelCallConfig(
                transcriber_config=self.transcriber_config,
                agent_config=self.agent_config,
                synthesizer_config=self.synthesizer_config,
                exotel_config=self.telephony_client.exotel_config,
                exotel_sid=self.telephony_id,
                from_phone=self.from_phone,
                to_phone=self.to_phone,
                output_to_speaker=False,
                sentry_tags=self.sentry_tags,
                telephony_params=self.telephony_params,
                direction="outbound",
            )
        else:
            raise ValueError("Unknown telephony client")
        await self.config_manager.save_config(self.conversation_id, call_config)
