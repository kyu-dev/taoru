from uuid import uuid4

from langchain.tools import tool

from taoru.infrastructure.memory_store import store


@tool
def save_learning_progress(topic: str, level: str, weak_points: list[str]) -> str:
    """Record a new learning-progress entry for a topic the user is studying.

    Adds an entry to the topic's history, it never overwrites past entries, so
    progress over time stays visible.

    Args:
        topic: Short slug identifying the topic, e.g. "langgraph_store".
        level: The user's current level on this topic, e.g. "beginner", "intermediate".
        weak_points: Specific points the user still struggles with.
    """
    namespace = ("topics", topic)
    store.put(namespace, str(uuid4()), {"level": level, "weak_points": weak_points})
    return f"Recorded progress for {topic}: level={level}."


@tool
def search_learning_progress(topic: str) -> str:
    """Read the full learning-progress history for a topic, oldest entry first.

    Use this before quizzing the user on a topic they've been tracked on, to see
    how they've progressed and which weak points to check again.

    Args:
        topic: Short slug identifying the topic, e.g. "langgraph_store".
    """
    namespace = ("topics", topic)
    entries = sorted(store.search(namespace), key=lambda item: item.created_at)

    if not entries:
        return f"No recorded progress for {topic}."

    return "\n".join(
        f"{entry.created_at:%Y-%m-%d}: level={entry.value['level']}, "
        f"weak_points={entry.value['weak_points']}"
        for entry in entries
    )


TOOLS = [save_learning_progress, search_learning_progress]
