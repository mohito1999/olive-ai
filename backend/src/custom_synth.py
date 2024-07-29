import asyncio
import io
import wave
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Type

import google.auth
from google.cloud import texttospeech_v1beta1 as tts  # type: ignore
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import (
    AzureSynthesizerConfig,
    CartesiaSynthesizerConfig,
    ElevenLabsSynthesizerConfig,
    GoogleSynthesizerConfig,
    PlayHtSynthesizerConfig,
    RimeSynthesizerConfig,
    StreamElementsSynthesizerConfig,
    SynthesizerConfig,
)
from vocode.streaming.synthesizer.abstract_factory import AbstractSynthesizerFactory
from vocode.streaming.synthesizer.azure_synthesizer import AzureSynthesizer
from vocode.streaming.synthesizer.base_synthesizer import (
    BaseSynthesizer,
    SynthesisResult,
)
from vocode.streaming.synthesizer.cartesia_synthesizer import CartesiaSynthesizer
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
from vocode.streaming.synthesizer.eleven_labs_websocket_synthesizer import (
    ElevenLabsWSSynthesizer,
)
from vocode.streaming.synthesizer.play_ht_synthesizer import PlayHtSynthesizer
from vocode.streaming.synthesizer.play_ht_synthesizer_v2 import PlayHtSynthesizerV2
from vocode.streaming.synthesizer.rime_synthesizer import RimeSynthesizer
from vocode.streaming.synthesizer.stream_elements_synthesizer import (
    StreamElementsSynthesizer,
)


class CustomGoogleSynthesizer(BaseSynthesizer[GoogleSynthesizerConfig]):
    def __init__(
        self,
        synthesizer_config: GoogleSynthesizerConfig,
    ):
        super().__init__(synthesizer_config)

        google.auth.default()

        # Instantiates a client
        self.client = tts.TextToSpeechClient()

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        self.voice = tts.VoiceSelectionParams(
            language_code=synthesizer_config.language_code,
            name=synthesizer_config.voice_name,
        )

        # Select the type of audio file you want returned
        self.audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16,
            sample_rate_hertz=synthesizer_config.sampling_rate,
            speaking_rate=synthesizer_config.speaking_rate,
            pitch=synthesizer_config.pitch,
            effects_profile_id=["telephony-class-application"],
        )
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)

    def synthesize(self, message: str) -> Any:
        if message.startswith("<"):
            synthesis_input = tts.SynthesisInput(ssml=message)
        else:
            synthesis_input = tts.SynthesisInput(text=message)

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        return self.client.synthesize_speech(
            request=tts.SynthesizeSpeechRequest(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config,
                enable_time_pointing=[tts.SynthesizeSpeechRequest.TimepointType.SSML_MARK],
            )
        )

    # TODO: make this nonblocking, see speech.TextToSpeechAsyncClient
    async def create_speech(
        self,
        message: BaseMessage,
        chunk_size: int,
        is_first_text_chunk: bool = False,
        is_sole_text_chunk: bool = False,
    ) -> SynthesisResult:
        response: tts.SynthesizeSpeechResponse = (  # type: ignore
            await asyncio.get_event_loop().run_in_executor(
                self.thread_pool_executor, self.synthesize, message.text
            )
        )
        output_sample_rate = response.audio_config.sample_rate_hertz

        output_bytes_io = io.BytesIO()
        in_memory_wav = wave.open(output_bytes_io, "wb")
        in_memory_wav.setnchannels(1)
        in_memory_wav.setsampwidth(2)
        in_memory_wav.setframerate(output_sample_rate)
        in_memory_wav.writeframes(response.audio_content[44:])
        output_bytes_io.seek(0)

        result = self.create_synthesis_result_from_wav(
            synthesizer_config=self.synthesizer_config,
            file=output_bytes_io,
            message=message,
            chunk_size=chunk_size,
        )
        return result


class CustomSynthesizerFactory(AbstractSynthesizerFactory):
    def create_synthesizer(
        self,
        synthesizer_config: SynthesizerConfig,
    ):
        if isinstance(synthesizer_config, AzureSynthesizerConfig):
            return AzureSynthesizer(synthesizer_config)
        elif isinstance(synthesizer_config, CartesiaSynthesizerConfig):
            return CartesiaSynthesizer(synthesizer_config)
        elif isinstance(synthesizer_config, ElevenLabsSynthesizerConfig):
            eleven_labs_synthesizer_class_type: Type[BaseSynthesizer] = ElevenLabsSynthesizer
            if synthesizer_config.experimental_websocket:
                eleven_labs_synthesizer_class_type = ElevenLabsWSSynthesizer
            return eleven_labs_synthesizer_class_type(synthesizer_config)
        elif isinstance(synthesizer_config, GoogleSynthesizerConfig):
            return CustomGoogleSynthesizer(synthesizer_config)
        elif isinstance(synthesizer_config, PlayHtSynthesizerConfig):
            if synthesizer_config.version == "2":
                return PlayHtSynthesizerV2(synthesizer_config)
            else:
                return PlayHtSynthesizer(synthesizer_config)
        elif isinstance(synthesizer_config, RimeSynthesizerConfig):
            return RimeSynthesizer(synthesizer_config)
        elif isinstance(synthesizer_config, StreamElementsSynthesizerConfig):
            return StreamElementsSynthesizer(synthesizer_config)
        else:
            raise Exception("Invalid synthesizer config")
