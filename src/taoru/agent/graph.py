from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from taoru.agent.agent_state import Agentstate
from taoru.agent.nodes.llm_call import llm_call
from taoru.agent.tools.obsidian_tools import TOOLS

agent_builder = StateGraph(Agentstate)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tools", ToolNode(TOOLS))
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", tools_condition, ["tools", END])
agent_builder.add_edge("tools", "llm_call")

#use by langgraph studio
graph = agent_builder.compile()
