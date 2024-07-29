from enum import Enum


class CampaignType(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class CampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class TelephonyServiceConfigClass(str, Enum):
    TWILIO = "TwilioConfig"
    EXOTEL = "ExotelConfig"


class AgentConfigClass(str, Enum):
    CHATGPT = "ChatGPTAgentConfig"
    GROQ = "GroqAgentConfig"
    LANGCHAIN = "LangchainAgentConfig"


class TranscriberConfigClass(str, Enum):
    DEEPGRAM = "DeepgramTranscriberConfig"


class SynthesizerConfigClass(str, Enum):
    GOOGLE = "GoogleSynthesizerConfig"
    AZURE = "AzureOpenAIConfig"
    ELEVEN_LABS = "ElevenLabsSynthesizerConfig"
