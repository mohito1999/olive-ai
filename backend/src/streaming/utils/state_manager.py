from typing import TYPE_CHECKING

from vocode.streaming.utils.state_manager import PhoneConversationStateManager
from streaming.telephony.client.exotel_client import ExotelClient

if TYPE_CHECKING:
    from streaming.telephony.conversation.exotel_phone_conversation import (
        ExotelPhoneConversation,
    )


class ExotelPhoneConversationStateManager(PhoneConversationStateManager):
    telephony_provider = "exotel"

    def __init__(self, conversation: "ExotelPhoneConversation"):
        super().__init__(conversation=conversation)
        self._exotel_phone_conversation = conversation

    def get_exotel_config(self):
        return self._exotel_phone_conversation.exotel_config

    def create_exotel_client(self):
        return ExotelClient(
            base_url=self._exotel_phone_conversation.base_url,
            maybe_exotel_config=self.get_exotel_config(),
        )

