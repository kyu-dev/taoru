from functools import reduce
from operator import add

from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage

from taoru.agent.agent_state import Agentstate
from taoru.agent.prompt import SYSTEM_PROMPT
from taoru.config import settings

model = init_chat_model(
    "mistralai:mistral-small-latest",
    api_key=settings.mistral_api_key.get_secret_value(),
)


def llm_call(state: Agentstate):
    """base node for llm conversation"""
    chunks = model.stream([SystemMessage(SYSTEM_PROMPT)] + state["messages"])
    # les AIMessageChunk s'additionnent en un AIMessage complet pour le state
    return {"messages": [reduce(add, chunks)]}
