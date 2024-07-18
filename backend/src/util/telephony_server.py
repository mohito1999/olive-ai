from config import (
    EXOTEL_ACCOUNT_SID,
    EXOTEL_API_KEY,
    EXOTEL_API_TOKEN,
    EXOTEL_APP_ID,
    EXOTEL_SUBDOMAIN,
)
from streaming.models.telephony import ExotelConfig

EXOTEL_CONFIG = ExotelConfig(
    account_sid=EXOTEL_ACCOUNT_SID,
    api_key=EXOTEL_API_KEY,
    api_token=EXOTEL_API_TOKEN,
    app_id=EXOTEL_APP_ID,
    subdomain=EXOTEL_SUBDOMAIN,
)

