
from typing import Any, AsyncGenerator, List, Mapping, Sequence

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, BaseChatMessage
from typing import Sequence
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient, SystemMessage, AssistantMessage, LLMMessage, UserMessage
from typing import Annotated, Optional, Union
from autogen_agentchat.base import Response, TaskResult, Team
from autogen_agentchat.messages import TextMessage
from pydantic import Field
from autogen_agentchat.state import SocietyOfMindAgentState
from autogen_core.model_context import UnboundedChatCompletionContext
import logging
from utils.logging_config import setup_logging, get_logger

class OriginTextMessage(TextMessage):
    origin: Optional[str]

class RetrievalMessage(OriginTextMessage):
    retrieval_success: Optional[bool]
    sourceUrls: Optional[List[str]]

    
DEFAULT_INSTRUCTION = "Earlier you were asked to fulfill a request. You and your team worked diligently to address that request. Here is a transcript of that conversation:"

DEFAULT_RESPONSE_PROMPT = (
    "Output a standalone response to the original request, without mentioning any of the intermediate discussion."
)
 
class GroupChatAgent(BaseChatAgent):
    def __init__(self, 
                *args, 
                name: str,
                team: Team,
                model_client : Optional[ChatCompletionClient]=None, 
                model_context=None,
                system_message: Optional[str] = None, 
                ngc=None, 
                description: str = "An agent that uses an inner team of agents to generate responses.", 
                instruction: str = DEFAULT_INSTRUCTION,
                response_prompt: str = DEFAULT_RESPONSE_PROMPT,
                llm_summary: bool = False,
                **kwargs) -> None:

        super().__init__(name=name, description=description)

        self._team = team
        self._model_client = model_client
        self._instruction = instruction
        self._response_prompt = response_prompt
        self._llm_summary = llm_summary
        

        if model_context is not None:
            self._model_context = model_context
        else:
            self._model_context = UnboundedChatCompletionContext()
        
        setup_logging()
        self.logger = get_logger(self.__class__.__name__)
    
    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        # Call the stream method and collect the messages.
        response: Response | None = None

        self.logger.notice(f"MESSAGES FROM ON_MESSAGES: {messages}")
        async for msg in self.on_messages_stream(messages, cancellation_token):
            if isinstance(msg, Response):
                response = msg
        assert response is not None
        return response

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        # Prepare the task for the team of agents.
        # Run the team of agents.
        result: TaskResult | None = None
        inner_messages: List[AgentEvent | ChatMessage] = []
        count = 0

        for message in messages:
            await self._model_context.add_message(message)
        
        task = await self._model_context.get_messages()

        self.logger.notice(f"THE TASK IS: {task}")
        async for inner_msg in self._team.run_stream(task=task, cancellation_token=cancellation_token):
            if isinstance(inner_msg, TaskResult):
                result = inner_msg
            else:
                count += 1
                if count <= len(task):
                    # Skip the task messages.
                    continue
                yield inner_msg
                inner_messages.append(inner_msg)
        assert result is not None

        if len(inner_messages) == 0:
            yield Response(
                chat_message=TextMessage(source=self.name, content="No response."), inner_messages=inner_messages
            )
        else:
            if self._llm_summary:
                # Generate a response using the model client.
                llm_messages: List[LLMMessage] = [SystemMessage(content=self._instruction)]
                llm_messages.extend(
                    [
                        UserMessage(content=message.content, source=message.source)
                        for message in inner_messages
                        if isinstance(message, BaseChatMessage)
                    ]
                )
                llm_messages.append(SystemMessage(content=self._response_prompt))
                completion = await self._model_client.create(messages=llm_messages, cancellation_token=cancellation_token)
                assert isinstance(completion.content, str)
                yield Response(
                    chat_message=TextMessage(source=self.name, content=completion.content, models_usage=completion.usage),
                    inner_messages=inner_messages,
                )
            else:
                self.logger.notice(f"LAST MESSAGE IS {inner_messages[-1]}")
                last_message = inner_messages[-1]

                if isinstance(last_message, RetrievalMessage):
                    yield Response(
                        chat_message=RetrievalMessage(
                            source=self.name,
                            content=last_message.content,
                            origin=last_message.origin,
                            retrieval_success=last_message.retrieval_success,
                            sourceUrls=last_message.sourceUrls,
                        )
                    )
                else:
                    yield Response(
                        chat_message=OriginTextMessage(source=self.name, content=last_message.content, origin=last_message.source),
                    )
        # Reset the team. This has to be verified. This has to be done in the bigger group chat
        #await self._team.reset()

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        try:
            await self._team.reset()
        except:
            await self._team._init(self._team._runtime)
            await self._team.reset()

    async def save_state(self) -> Mapping[str, Any]:
        try:
            team_state = await self._team.save_state()
        except:
            await self._team._init(self._team._runtime)
        
        team_state = await self._team.save_state()
        state = SocietyOfMindAgentState(inner_team_state=team_state)
        return state.model_dump()

    async def load_state(self, state: Mapping[str, Any]) -> None:

        society_of_mind_state = SocietyOfMindAgentState.model_validate(state)
        await self._team.load_state(society_of_mind_state.inner_team_state)