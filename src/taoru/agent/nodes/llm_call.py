from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage

from taoru.agent.agent_state import Agentstate
from taoru.agent.prompt import SYSTEM_PROMPT
from taoru.agent.tools import TOOLS

model = init_chat_model(
    model="qwen3.8:27b-mlx",
    model_provider="ollama",
).bind_tools(TOOLS)


def llm_call(state: Agentstate):
    """base node for llm conversation"""
    response = model.invoke([SystemMessage(SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}
