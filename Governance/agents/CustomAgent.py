
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage
from typing import Sequence
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient,  SystemMessage, AssistantMessage, UserMessage
from typing import Annotated, Optional, Union
from autogen_agentchat.base import Response
from autogen_agentchat.state import AssistantAgentState
from autogen_core.model_context import UnboundedChatCompletionContext
import time
from typing import Any, Mapping
from Governance.utils.logging_config import setup_logging, get_logger
import time

class CustomAgent(BaseChatAgent):
    def __init__(self, *args, model_client : Optional[ChatCompletionClient]=None, system_message: Optional[str] = None, ngc=None, model_context=None, **kwargs) -> None:
        super(CustomAgent, self).__init__(*args, **kwargs)

        if model_client is not None:
            self._model_client = model_client
            try:
                self._model_name = model_client._raw_config['azure_deployment']
            except:
                self._model_name = None

        if system_message is not None:
            self._system_messages = [SystemMessage(content=system_message)]

        if ngc is not None:
            self.ngc = ngc

        if model_context is not None:
            self._model_context = model_context
        else:
            self._model_context = UnboundedChatCompletionContext()
        
        setup_logging()
        self.logger = get_logger(self.__class__.__name__)
    
    async def _llm_response(self, messages: Union[ChatMessage,Sequence[ChatMessage]]) -> Response:

        for msg in messages:
            if msg.source != "user":
                await self._model_context.add_message(AssistantMessage(content=msg.content, source=msg.source))
            else:
                await self._model_context.add_message(UserMessage(content=msg.content, source=msg.source))
        
        llm_messages = self._system_messages + await self._model_context.get_messages()

        start = time.time()
        response = await self._model_client.create(llm_messages)
        end = time.time()

        if self._model_name is not None:
            self.logger.notice(f"service=openai, deployment={self._model_name}, time_ms={int((end-start)*1000)}")

        return response


    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

    async def save_state(self) -> Mapping[str, Any]:
        """Save the current state of the assistant agent."""
        model_context_state = await self._model_context.save_state()
        return AssistantAgentState(llm_context=model_context_state).model_dump()

    async def load_state(self, state: Mapping[str, Any]) -> None:
        """Load the state of the assistant agent"""
        assistant_agent_state = AssistantAgentState.model_validate(state)
        # Load the model context state.
        await self._model_context.load_state(assistant_agent_state.llm_context)

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

