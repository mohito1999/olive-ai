from enum import Enum


class CampaignType(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class CampaignStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"


class CampaignAction(str, Enum):
    START = "START"
    STOP = "STOP"
    TEST = "TEST"


class TelephonyServiceConfigClass(str, Enum):
    TWILIO = "TwilioConfig"
    EXOTEL = "ExotelConfig"


class AgentConfigClass(str, Enum):
    CHATGPT = "ChatGPTAgentConfig"
    GROQ = "GroqAgentConfig"
    LANGCHAIN = "LangchainAgentConfig"


class AgentActionConfigClass(str, Enum):
    STORE_REMARK = "StoreRemarkActionConfig"


class TranscriberConfigClass(str, Enum):
    DEEPGRAM = "DeepgramTranscriberConfig"


class SynthesizerConfigClass(str, Enum):
    GOOGLE = "GoogleSynthesizerConfig"
    AZURE = "AzureOpenAIConfig"
    ELEVEN_LABS = "ElevenLabsSynthesizerConfig"
