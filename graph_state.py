# graph_state.py
from typing import List, TypedDict
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    topic: str
    messages: List[BaseMessage]
    summary: str
    round_count: int
    winner: str
    justification: str