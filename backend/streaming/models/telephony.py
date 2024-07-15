from enum import Enum
from typing import Any, Dict, Optional

from vocode.streaming.models.telephony import BaseCallConfig, TelephonyProviderConfig
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.telephony.constants import DEFAULT_SAMPLING_RATE
from streaming.telephony.constants import EXOTEL_AUDIO_ENCODING, EXOTEL_CHUNK_SIZE


class CustomCallConfigType(str, Enum):
    BASE = "call_config_base"
    TWILIO = "call_config_twilio"
    VONAGE = "call_config_vonage"
    EXOTEL = "call_config_exotel"

DEFAULT_EXOTEL_SUBDOMAIN = "api.exotel.com"

class ExotelConfig(TelephonyProviderConfig):
    account_sid: str
    api_key: str
    api_token: str
    subdomain: str = DEFAULT_EXOTEL_SUBDOMAIN
    app_id: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = {}


class ExotelCallConfig(BaseCallConfig, type=CustomCallConfigType.EXOTEL.value):
    exotel_config: ExotelConfig
    exotel_sid: str

    @staticmethod
    def default_transcriber_config():
        return DeepgramTranscriberConfig(
            sampling_rate=DEFAULT_SAMPLING_RATE,
            audio_encoding=EXOTEL_AUDIO_ENCODING,
            chunk_size=EXOTEL_CHUNK_SIZE,
            model="phonecall",
            tier="nova",
            endpointing_config=PunctuationEndpointingConfig(),
        )

    @staticmethod
    def default_synthesizer_config():
        return AzureSynthesizerConfig(
            sampling_rate=DEFAULT_SAMPLING_RATE,
            audio_encoding=EXOTEL_AUDIO_ENCODING,
        )
