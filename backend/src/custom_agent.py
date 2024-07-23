from typing import AsyncGenerator, AsyncIterator, Literal, Optional, Sequence, Type

import sentry_sdk
from langchain_core.messages.base import BaseMessage as LangchainBaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from loguru import logger

# from pydantic import Field
from pydantic.v1 import BaseModel, Field
from vocode.streaming.action.abstract_factory import AbstractActionFactory
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.action.default_factory import CONVERSATION_ACTIONS
from vocode.streaming.agent.abstract_factory import AbstractAgentFactory
from vocode.streaming.agent.anthropic_agent import AnthropicAgent
from vocode.streaming.agent.base_agent import BaseAgent, GeneratedResponse, StreamedResponse
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.agent.echo_agent import EchoAgent
from vocode.streaming.agent.groq_agent import GroqAgent
from vocode.streaming.agent.langchain_agent import LangchainAgent
from vocode.streaming.agent.restful_user_implemented_agent import (
    RESTfulUserImplementedAgent,
)
from vocode.streaming.agent.streaming_utils import (
    collate_response_async,
    stream_response_async,
)
from vocode.streaming.models.actions import ActionConfig as VocodeActionConfig
from vocode.streaming.models.actions import ActionInput, ActionOutput
from vocode.streaming.models.agent import (
    AgentConfig,
    AnthropicAgentConfig,
    ChatGPTAgentConfig,
    ChatVertexAIAgentConfig,
    EchoAgentConfig,
    GroqAgentConfig,
    LangchainAgentConfig,
    RESTfulUserImplementedAgentConfig,
)
from vocode.streaming.models.message import BaseMessage, LLMToken
from vocode.utils.sentry_utils import CustomSentrySpans, sentry_create_span

from custom_langchain import custom_init_chat_model

################################################
# Implementation that fixes Google Vertex AI two-way chat
################################################
# class CustomLangchainAgent(LangchainAgent):
#     def format_langchain_messages_from_transcript(self) -> list[tuple]:
#         if not self.transcript:
#             raise ValueError("A transcript is not attached to the agent")
#         messages = []
#         for event_log in self.transcript.event_logs:
#             if isinstance(event_log, Message):
#                 last_message_sender = messages[-1][0] if messages else None
#                 if event_log.sender == Sender.BOT:
#                     if last_message_sender == "ai":
#                         messages[-1] = (
#                             "ai",
#                             f"{messages[-1][1]} {event_log.to_string(include_sender=False)}",
#                         )
#                     else:
#                         messages.append(("ai", event_log.to_string(include_sender=False)))
#                 elif event_log.sender == Sender.HUMAN:
#                     if last_message_sender == "human":
#                         messages[-1] = (
#                             "human",
#                             f"{messages[-1][1]} {event_log.to_string(include_sender=False)}",
#                         )
#                     else:
#                         messages.append(
#                             ("human", event_log.to_string(include_sender=False))
#                         )
#             else:
#                 raise ValueError(
#                     f"Invalid event log type {type(event_log)}. Langchain currently only supports human and bot messages"
#                 )
#
#         if self.agent_config.provider == "anthropic":
#             messages = merge_bot_messages_for_langchain(messages)
#
#         return messages


class CustomLangchainAgent(LangchainAgent):
    async def generate_response(
        self,
        human_input,
        conversation_id: str,
        is_interrupt: bool = False,
        bot_was_in_medias_res: bool = False,
    ) -> AsyncGenerator[GeneratedResponse, None]:
        if not self.transcript:
            raise ValueError("A transcript is not attached to the agent")
        try:
            first_sentence_total_span = sentry_create_span(
                sentry_callable=sentry_sdk.start_span,
                op=CustomSentrySpans.LLM_FIRST_SENTENCE_TOTAL,
            )

            ttft_span = sentry_create_span(
                sentry_callable=sentry_sdk.start_span,
                op=CustomSentrySpans.TIME_TO_FIRST_TOKEN,
            )
            stream = self.chain.astream(
                {"chat_history": self.format_langchain_messages_from_transcript()},
                {"configurable": {"thread_id": 42}},
            )
        except Exception as e:
            logger.error(
                "Error while hitting Langchain",
                exc_info=True,
            )
            raise e

        response_generator = collate_response_async

        using_input_streaming_synthesizer = (
            self.conversation_state_manager.using_input_streaming_synthesizer()
        )
        if using_input_streaming_synthesizer:
            response_generator = stream_response_async
        async for message in response_generator(
            conversation_id=conversation_id,
            gen=self.token_generator(
                stream,
            ),
            sentry_span=ttft_span,
        ):
            if first_sentence_total_span:
                first_sentence_total_span.finish()

            ResponseClass = (
                StreamedResponse
                if using_input_streaming_synthesizer
                else GeneratedResponse
            )
            MessageType = LLMToken if using_input_streaming_synthesizer else BaseMessage

            if isinstance(message, str):
                yield ResponseClass(
                    message=MessageType(text=message),
                    is_interruptible=True,
                )
            else:
                yield ResponseClass(
                    message=message,
                    is_interruptible=True,
                )

    async def token_generator(
        self,
        gen: AsyncIterator[LangchainBaseMessage],
    ) -> AsyncGenerator[str, None]:
        async for chunk in gen:
            logger.debug(f"Chunk: {chunk}")
            agent_chunk = chunk.get("agent")
            tools_chunk = chunk.get("tools")

            if agent_chunk:
                last_message = agent_chunk["messages"][-1]
                if isinstance(last_message.content, str):
                    yield last_message.content
                else:
                    raise ValueError(
                        f"Received unexpected message type {type(chunk)} from Langchain. Expected str."
                    )
            if tools_chunk:
                last_message = tools_chunk["messages"][-1]
                if isinstance(last_message.content, str):
                    yield last_message.content
                else:
                    raise ValueError(
                        f"Received unexpected message type {type(chunk)} from Langchain. Expected str."
                    )


@tool
def search_the_internet(query: str):
    """Search a query on the internet"""
    logger.warning(query)
    return "This is what I found!"


class LogToConsoleParameters(BaseModel):
    message: str = Field(..., description="Message to log to console")


class LogToConsoleResponse(BaseModel):
    message: str = Field(..., description="Message to return to the user")


class LogToConsoleActionConfig(
    VocodeActionConfig,
    type="action_log_message_to_console",  # type: ignore
):
    pass

class LogToConsoleAction(
    BaseAction[
        LogToConsoleActionConfig,
        LogToConsoleParameters,
        LogToConsoleResponse,
    ]
):
    description: str = """Log a message to the server console.
    The input to this action is a message string, and the output is a message which can be returned to the user.
    """
    parameters_type: Type[LogToConsoleParameters] = LogToConsoleParameters
    response_type: Type[LogToConsoleResponse] = LogToConsoleResponse

    def __init__(
        self,
        action_config: LogToConsoleActionConfig,
    ):
        super().__init__(
            action_config,
            should_respond="sometimes",
            quiet=False,
            is_interruptible=True,
        )

    async def run(
        self, action_input: ActionInput[LogToConsoleParameters]
    ) -> ActionOutput[LogToConsoleResponse]:
        message = action_input.params.message
        logger.warning(message)
        return ActionOutput(
            action_type=action_input.action_config.type,
            response=LogToConsoleResponse(message="Logged message successfully to console"),
        )


class CustomActionFactory(AbstractActionFactory):
    def __init__(self, actions: Sequence[VocodeActionConfig] | dict = {}):
        self.action_configs_dict = {action.type: action for action in actions}
        self.action_configs_dict.update(
            {
                "action_log_message_to_console": LogToConsoleActionConfig(
                    type="action_log_message_to_console"
                )
            }
        )
        self.actions = {
            **CONVERSATION_ACTIONS,
            "action_log_message_to_console": LogToConsoleAction,
        }

    def create_action(self, action_config: VocodeActionConfig):
        if action_config.type not in self.action_configs_dict:
            raise Exception("Action type not supported by Agent config.")

        action_class = self.actions[action_config.type]

        return action_class(action_config)


class CustomAgentFactory(AbstractAgentFactory):
    def create_agent(self, agent_config: AgentConfig) -> BaseAgent:
        if isinstance(agent_config, ChatGPTAgentConfig):
            return ChatGPTAgent(agent_config=agent_config, action_factory=CustomActionFactory())
        elif isinstance(agent_config, EchoAgentConfig):
            return EchoAgent(agent_config=agent_config)
        elif isinstance(agent_config, RESTfulUserImplementedAgentConfig):
            return RESTfulUserImplementedAgent(agent_config=agent_config)
        elif isinstance(agent_config, GroqAgentConfig):
            return GroqAgent(
                agent_config=agent_config, action_factory=CustomActionFactory()
            )
        elif isinstance(agent_config, AnthropicAgentConfig):
            return AnthropicAgent(agent_config=agent_config)
        elif isinstance(agent_config, LangchainAgentConfig):
            messages_for_prompt_template = [("placeholder", "{chat_history}")]
            if agent_config.prompt_preamble:
                messages_for_prompt_template.insert(
                    0, ("system", agent_config.prompt_preamble)
                )
            prompt_template = ChatPromptTemplate.from_messages(
                messages_for_prompt_template
            )
            model = custom_init_chat_model(
                model=agent_config.model_name,
                model_provider=agent_config.provider,
                temperature=agent_config.temperature,
                # max_tokens=agent_config.max_tokens,
                # location="asia-south1",
            )
            tools = [search_the_internet]
            tool_node = ToolNode(tools)
            model_with_tools = model.bind_tools(tools)

            def should_continue(state: MessagesState) -> Literal["tools", END]:
                messages = state["messages"]
                last_message = messages[-1]
                logger.debug(f"tool_calls: {last_message.tool_calls}")
                if last_message.tool_calls:
                    return "tools"
                return END

            def call_model(state: MessagesState):
                messages = state["messages"]
                response = model_with_tools.invoke(messages)
                return {"messages": [response]}

            workflow = StateGraph(MessagesState)

            workflow.add_node("agent", call_model)
            workflow.add_node("tools", tool_node)

            workflow.set_entry_point("agent")
            workflow.add_conditional_edges(
                "agent",
                should_continue,
            )

            workflow.add_edge("tools", "agent")
            # checkpointer = MemorySaver()
            app = workflow.compile()

            # chain = prompt_template | app
            chain = prompt_template | model

            return LangchainAgent(
                agent_config=agent_config,
                chain=chain,
            )
            # return CustomLangchainAgent(
            #     agent_config=agent_config,
            #     chain=chain,
            # )
        raise Exception("Invalid agent config", agent_config.type)
