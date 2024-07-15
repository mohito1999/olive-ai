import os
import aiohttp
from typing import Dict, Optional

from loguru import logger

from vocode.streaming.telephony.client.abstract_telephony_client import (
    AbstractTelephonyClient,
)
from vocode.streaming.utils.async_requester import AsyncRequestor

from streaming.models.telephony import ExotelConfig


class ExotelBadRequestException(ValueError):
    pass


class ExotelException(ValueError):
    pass


class ExotelClient(AbstractTelephonyClient):
    def __init__(
        self,
        base_url,
        maybe_exotel_config: Optional[ExotelConfig] = None,
    ):
        self.exotel_config = maybe_exotel_config or ExotelConfig(
            app_id=os.environ["EXOTEL_APP_ID"],
            account_sid=os.environ["EXOTEL_ACCOUNT_SID"],
            api_key=os.environ["EXOTEL_API_KEY"],
            api_token=os.environ["EXOTEL_API_TOKEN"],
        )
        self.auth = aiohttp.BasicAuth(
            login=self.exotel_config.api_key,
            password=self.exotel_config.api_token,
        )
        super().__init__(base_url=base_url)

    def get_telephony_config(self):
        return self.exotel_config

    async def create_call(
        self,
        conversation_id: str,
        to_phone: str,
        from_phone: str,
        record: bool = False,  # currently no-op
        digits: Optional[str] = None,  # currently no-op
        telephony_params: Optional[Dict[str, str]] = None,
    ) -> str:
        logger.debug(f"Creating call to {to_phone} from {from_phone}")
        data = {
            "From": to_phone,
            "CallerId": from_phone,
            "Url": f"http://my.exotel.com/{self.exotel_config.account_sid}/exoml/start_voice/{self.exotel_config.app_id}",
            **(telephony_params or {}),
        }
        async with AsyncRequestor().get_session().post(
            f"https://{self.exotel_config.subdomain}/v1/Accounts/{self.exotel_config.account_sid}/Calls/connect.json",
            auth=self.auth,
            data=data,
        ) as response:
            if not response.ok:
                if response.status == 400:
                    logger.error(
                        f"Failed to create call: {response.status} {response.reason} {await response.json()}"
                    )
                    raise ExotelBadRequestException(
                        "Telephony provider rejected call; this is usually due to a bad/malformed number. "
                    )
                else:
                    logger.error(
                        f"Failed to create call: {response.status} {response.reason} {await response.json()}"
                    )
                    raise ExotelException(
                        f"Exotel failed to create call: {response.status} {response.reason}"
                    )
            exotel_response = await response.json()
            call_sid = exotel_response["Call"]["Sid"]
            return call_sid

    @staticmethod
    def create_call_exotel(base_url, conversation_id, is_outbound: bool = False):
        return {"url": f"wss://{base_url}/connect_call/{conversation_id}"}

    async def end_call(self, twilio_sid):
        pass
        # async with AsyncRequestor().get_session().post(
        #     f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_config.account_sid}/Calls/{twilio_sid}.json",
        #     auth=self.auth,
        #     data={"Status": "completed"},
        # ) as response:
        #     if not response.ok:
        #         raise RuntimeError(f"Failed to end call: {response.status} {response.reason}")
        #     response = await response.json()
        #     return response["status"] == "completed"
