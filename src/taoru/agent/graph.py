from langgraph.graph import END, START, StateGraph

from taoru.agent.agent_state import Agentstate
from taoru.agent.nodes.llm_call import llm_call

agent_builder = StateGraph(Agentstate)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_edge("llm_call", END)

graph = agent_builder.compile()
