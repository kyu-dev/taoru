"""Taoru's REPL: streams the agent's tokens live, shows tool calls as they happen,
and pauses for approval when the graph hits a guarded tool.
"""

import uuid

from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from taoru.agent.graph import agent_builder

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
YELLOW = "\033[33m"

BANNER = f"""{CYAN}{BOLD}
 ████████╗ █████╗  ██████╗ ██████╗ ██╗   ██╗
 ╚══██╔══╝██╔══██╗██╔═══██╗██╔══██╗██║   ██║
    ██║   ███████║██║   ██║██████╔╝██║   ██║
    ██║   ██╔══██║██║   ██║██╔══██╗██║   ██║
    ██║   ██║  ██║╚██████╔╝██║  ██║╚██████╔╝
    ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝
{RESET}{DIM}At your service, Arthur. Type 'exit' to leave.{RESET}
"""

# "messages" streams LLM tokens as they're generated; "updates" streams each
# node's output (AIMessage.tool_calls, ToolMessage results, and __interrupt__).
# Passing both as a list interleaves them in one loop instead of two separate runs.
STREAM_MODES = ["messages", "updates"]


def _format_args(args: dict) -> str:
    return ", ".join(f"{k}={v!r}" for k, v in args.items())


def _handle_update(update: dict) -> dict | None:
    """Print tool activity from an 'updates' chunk. Returns the interrupt payload, if any."""
    if "__interrupt__" in update:
        return update["__interrupt__"][0].value

    for node_name, node_update in update.items():
        for message in node_update.get("messages", []):
            if getattr(message, "tool_calls", None):
                for call in message.tool_calls:
                    print(f"{YELLOW}  \U0001f527 {call['name']}({_format_args(call['args'])}){RESET}")
            elif node_name == "tools":
                content = str(message.content)
                preview = content if len(content) <= 200 else content[:200] + "…"
                print(f"{DIM}     -> {preview}{RESET}")
    return None


def _ask_approval(action: str, args: dict) -> dict:
    prompt = f"{MAGENTA}Taoru wants to run {action}({_format_args(args)}). Approve? [y/N] {RESET}"
    return {"action": "approve" if input(prompt).strip().lower() == "y" else "deny"}


def _run_turn(graph, stream_input, config) -> None:
    """Stream one turn, printing tokens live. Recurses once per interrupt hit."""
    printed_prefix = False
    for mode, payload in graph.stream(stream_input, config, stream_mode=STREAM_MODES):
        if mode == "messages":
            chunk, _metadata = payload
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                if not printed_prefix:
                    print(f"{CYAN}{BOLD}Taoru:{RESET} ", end="", flush=True)
                    printed_prefix = True
                print(chunk.content, end="", flush=True)
        elif mode == "updates":
            interrupt_payload = _handle_update(payload)
            if interrupt_payload is not None:
                print()
                decision = _ask_approval(interrupt_payload["action"], interrupt_payload["args"])
                _run_turn(graph, Command(resume=decision), config)
                return
    print()


def main() -> None:
    graph = agent_builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print(BANNER)
    while True:
        try:
            user_input = input(f"{BOLD}You:{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        _run_turn(graph, {"messages": [("user", user_input)]}, config)


if __name__ == "__main__":
    main()
