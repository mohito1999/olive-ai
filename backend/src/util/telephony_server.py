from vocode.streaming.models.telephony import TwilioConfig

from config import (
    EXOTEL_ACCOUNT_SID,
    EXOTEL_API_KEY,
    EXOTEL_API_TOKEN,
    EXOTEL_APP_ID,
    EXOTEL_SUBDOMAIN,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)
from streaming.models.telephony import ExotelConfig

EXOTEL_CONFIG = ExotelConfig(
    account_sid=EXOTEL_ACCOUNT_SID,
    api_key=EXOTEL_API_KEY,
    api_token=EXOTEL_API_TOKEN,
    app_id=EXOTEL_APP_ID,
    subdomain=EXOTEL_SUBDOMAIN,
)

TWILIO_CONFIG = TwilioConfig(
    account_sid=TWILIO_ACCOUNT_SID,
    auth_token=TWILIO_AUTH_TOKEN
)
