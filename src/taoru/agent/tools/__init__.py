from taoru.agent.tools.guardrails import confirm_dangerous_tools
from taoru.agent.tools.memory_tools import TOOLS as MEMORY_TOOLS
from taoru.agent.tools.obsidian_tools import TOOLS as OBSIDIAN_TOOLS
from taoru.agent.tools.rag_tools import TOOLS as RAG_TOOLS

TOOLS = OBSIDIAN_TOOLS + RAG_TOOLS + MEMORY_TOOLS
