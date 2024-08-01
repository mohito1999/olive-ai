from datetime import datetime
from typing import Type

from pydantic.v1 import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import ActionConfig as VocodeActionConfig
from vocode.streaming.models.actions import ActionInput, ActionOutput

from log import log
from models import Call, get_db
from repositories import CallRepository
from schemas import CallActionSchema

ACTION_STORE_REMARK_TYPE = "action_store_remark"
DEFAULT_STORE_REMARK_ACTION_DESCRIPTION = """Store a remark in the database that is useful to the context of the conversation. {user_description}
The input to this action is a remark message string which should be stored in the database. It has no output."""


class StoreRemarkParameters(BaseModel):
    remark_message: str = Field(..., description="Remark message to store in the database")


class StoreRemarkResponse(BaseModel):
    pass


class StoreRemarkActionConfig(
    VocodeActionConfig,
    type=ACTION_STORE_REMARK_TYPE,  # type: ignore
):
    description: str = ""


class StoreRemarkAction(
    BaseAction[
        StoreRemarkActionConfig,
        StoreRemarkParameters,
        StoreRemarkResponse,
    ]
):
    description: str = DEFAULT_STORE_REMARK_ACTION_DESCRIPTION
    parameters_type: Type[StoreRemarkParameters] = StoreRemarkParameters
    response_type: Type[StoreRemarkResponse] = StoreRemarkResponse

    def __init__(
        self,
        action_config: StoreRemarkActionConfig,
    ):
        super().__init__(
            action_config,
            should_respond="sometimes",
            quiet=False,
            is_interruptible=True,
        )
        self.description = self.description.format(user_description=action_config.description)
        log.warning(f"StoreRemarkAction created with description: {self.description}")

    async def run(
        self, action_input: ActionInput[StoreRemarkParameters]
    ) -> ActionOutput[StoreRemarkResponse]:
        db_gen = get_db()
        db: AsyncSession = await db_gen.__anext__()

        action = CallActionSchema(
            type=action_input.action_config.type,
            data={"message": action_input.params.remark_message, "timestamp": datetime.utcnow().isoformat()},
        )
        await CallRepository(db).update(values={"actions": Call.actions + [action.dict()]}, id=action_input.conversation_id)

        return ActionOutput(
            action_type=action_input.action_config.type,
            response=StoreRemarkResponse(),
        )
