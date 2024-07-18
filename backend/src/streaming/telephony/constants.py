
from vocode.streaming.models.audio import AudioEncoding
from vocode.streaming.telephony.constants import DEFAULT_SAMPLING_RATE

EXOTEL_CHUNK_SIZE = DEFAULT_SAMPLING_RATE.value // 10
EXOTEL_AUDIO_ENCODING = AudioEncoding.LINEAR16

