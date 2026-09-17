from langchain_core.messages import ToolMessage
from langgraph.types import interrupt

DANGEROUS_TOOLS = {"edit_obsidian_note", "delete_obsidian_note"}


def confirm_dangerous_tools(request, execute):
    """wrap_tool_call for ToolNode: pause for approval before a dangerous tool runs."""
    if request.tool_call["name"] in DANGEROUS_TOOLS:
        decision = interrupt({
            "action": request.tool_call["name"],
            "args": request.tool_call["args"],
        })
        if decision.get("action") != "approve":
            return ToolMessage(
                content="Cancelled by user.",
                name=request.tool_call["name"],
                tool_call_id=request.tool_call["id"],
            )
    return execute(request)
