from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage

from taoru.agent.agent_state import Agentstate
from taoru.agent.prompt import SYSTEM_PROMPT
from taoru.config import settings
from taoru.agent.tools.obsidian_tools import TOOLS

model = init_chat_model(
    "mistralai:mistral-small-latest",
    api_key=settings.mistral_api_key.get_secret_value(),
).bind_tools(TOOLS)


def llm_call(state: Agentstate):
    """base node for llm conversation"""
    response = model.invoke([SystemMessage(SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}
