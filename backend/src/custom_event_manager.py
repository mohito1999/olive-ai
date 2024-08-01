from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from vocode.streaming.models.events import (
    ActionEvent,
    Event,
    EventType,
    PhoneCallConnectedEvent,
    PhoneCallDidNotConnectEvent,
    PhoneCallEndedEvent,
)
from vocode.streaming.models.transcript import TranscriptCompleteEvent
from vocode.streaming.utils.events_manager import EventsManager

from constants import CallStatus
from exceptions import DatabaseException
from log import log
from models import get_db
from repositories import CallRepository


class CustomEventsManager(EventsManager):
    def __init__(self):
        super().__init__(
            [
                EventType.TRANSCRIPT_COMPLETE,
                EventType.ACTION,
                EventType.PHONE_CALL_CONNECTED,
                EventType.PHONE_CALL_DID_NOT_CONNECT,
                EventType.PHONE_CALL_ENDED,
            ]
        )

    async def handle_event(self, event: Event):
        log.warning(f"Received event {type(event)} for conversation {event.conversation_id}")

        db_gen = get_db()
        db: AsyncSession = await db_gen.__anext__()

        try:
            if isinstance(event, ActionEvent):
                log.warning(f"[Action event] {event.action_input} {event.action_output}")
            if isinstance(event, TranscriptCompleteEvent):
                await CallRepository(db).update(
                    values={"transcript": event.transcript.to_string()}, id=event.conversation_id
                )
            if isinstance(event, PhoneCallConnectedEvent):
                await CallRepository(db).update(
                    values={"start_time": datetime.utcnow(), "status": CallStatus.IN_PROGRESS.value},
                    id=event.conversation_id,
                )
            if isinstance(event, PhoneCallDidNotConnectEvent):
                log.warning(
                    f"[Phone call did not connect event] {event.to_phone_number} -> {event.from_phone_number}"
                )
            if isinstance(event, PhoneCallEndedEvent):
                await CallRepository(db).update(
                    values={"end_time": datetime.utcnow(), "status": CallStatus.COMPLETED.value},
                    id=event.conversation_id,
                )
        except DatabaseException as e:
            log.error(f"Error handling event {type(event)}: {e}")

