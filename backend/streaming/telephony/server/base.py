from vocode.streaming.telephony.server.base import AbstractInboundCallConfig

from streaming.models.telephony import ExotelConfig

class ExotelInboundCallConfig(AbstractInboundCallConfig):
    exotel_config: ExotelConfig

