from __future__ import annotations

import asyncio
import base64
import json
from typing import Optional

from fastapi import WebSocket

from vocode.streaming.output_device.abstract_output_device import AbstractOutputDevice
from vocode.streaming.telephony.constants import DEFAULT_SAMPLING_RATE
from streaming.telephony.constants import EXOTEL_AUDIO_ENCODING


class ExotelOutputDevice(AbstractOutputDevice):
    def __init__(
        self, ws: Optional[WebSocket] = None, stream_sid: Optional[str] = None
    ):
        super().__init__(
            sampling_rate=DEFAULT_SAMPLING_RATE, audio_encoding=EXOTEL_AUDIO_ENCODING
        )
        self.ws = ws
        self.stream_sid = stream_sid
        self.active = True
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        # self.process_task = asyncio.create_task(self.process())

    async def process(self):
        while self.active:
            message = await self.queue.get()
            await self.ws.send_text(message)

    def consume_nonblocking(self, chunk: bytes):
        exotel_message = {
            "event": "media",
            "stream_sid": self.stream_sid,
            "media": {"payload": base64.b64encode(chunk).decode("utf-8")},
        }
        self.queue.put_nowait(json.dumps(exotel_message))

    def maybe_send_mark_nonblocking(self, message_sent):
        mark_message = {
            "event": "mark",
            "stream_sid": self.stream_sid,
            "mark": {
                "name": "Sent {}".format(message_sent),
            },
        }
        self.queue.put_nowait(json.dumps(mark_message))

    # def terminate(self):
    #     self.process_task.cancel()
