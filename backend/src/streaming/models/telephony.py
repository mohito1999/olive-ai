from enum import Enum
from typing import Any, Dict, Optional

from vocode.streaming.models.client_backend import OutputAudioConfig
from vocode.streaming.models.synthesizer import (
    AzureSynthesizerConfig,
    GoogleSynthesizerConfig,
)
from vocode.streaming.models.telephony import BaseCallConfig, TelephonyProviderConfig
from vocode.streaming.models.transcriber import (
    DEFAULT_SAMPLING_RATE,
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramEndpointingConfig

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
            language="hi",
            model="nova-2",
            sampling_rate=DEFAULT_SAMPLING_RATE.value,
            audio_encoding=EXOTEL_AUDIO_ENCODING,
            chunk_size=EXOTEL_CHUNK_SIZE,
            endpointing_config=DeepgramEndpointingConfig(),
        )

    @staticmethod
    def default_synthesizer_config():
        return GoogleSynthesizerConfig.from_output_audio_config(
            output_audio_config=OutputAudioConfig(
                sampling_rate=DEFAULT_SAMPLING_RATE.value,
                audio_encoding=EXOTEL_AUDIO_ENCODING,
            ),
            language_code="hi-IN",
            voice_name="hi-IN-Wavenet-B",
            pitch=-10.0,
        )
