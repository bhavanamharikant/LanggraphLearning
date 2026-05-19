# Demonstrating state with custom reducers

from typing import Annotated, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, START, END


# ✅ Reducers

def min_reducer(existing: int, new: int) -> int:
    return min(existing, new)


def max_reducer(existing: int, new: int) -> int:
    return max(existing, new)


def datetime_max_reducer(existing: datetime, new: datetime) -> datetime:
    return max(existing, new)


def dict_merge_reducer(existing: dict[str, str], new: dict[str, str]) -> dict[str, str]:
    return {**existing, **new}


def set_union_reducer(existing: set[int], new: set[int]) -> set[int]:
    return existing | new


# ✅ Workflow state

class WorkflowState(TypedDict):
    min_cost: Annotated[int, min_reducer]
    max_score: Annotated[int, max_reducer]
    latest_update: Annotated[datetime, datetime_max_reducer]
    metadata: Annotated[dict[str, str], dict_merge_reducer]
    unique_ids: Annotated[set[int], set_union_reducer]


# ✅ Example nodes

def node_a(state: WorkflowState):
    return {
        "min_cost": 50,
        "max_score": 80,
        "latest_update": datetime.now(),
        "metadata": {"source": "node_a"},
        "unique_ids": {1, 2}
    }


def node_b(state: WorkflowState):
    return {
        "min_cost": 30,
        "max_score": 90,
        "latest_update": datetime.now(),
        "metadata": {"status": "processed"},
        "unique_ids": {2, 3}
    }


# ✅ Graph

graph_builder = StateGraph(WorkflowState)

graph_builder.add_node("node_a", node_a)
graph_builder.add_node("node_b", node_b)

graph_builder.add_edge(START, "node_a")
graph_builder.add_edge("node_a", "node_b")
graph_builder.add_edge("node_b", END)

graph = graph_builder.compile()


# ✅ Initial state (important!)

initial_state = {
    "min_cost": 100,
    "max_score": 0,
    "latest_update": datetime.now(),
    "metadata": {},
    "unique_ids": set()
}


final_state = graph.invoke(initial_state)

print(final_state)



# Demonstrating add_messages reducer

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def node1(state: ChatState):
    return {"messages": [HumanMessage(content="Hello there!")]}


def node2(state: ChatState):
    return {"messages": [AIMessage(content="Hi! How can I assist you today?")]}


def node3(state: ChatState):
    return {"messages": ["Hello"]}


def node4(state: ChatState):
    return {"messages": [{"type": "human", "content": "What can you do?"}]}


graph_builder = StateGraph(ChatState)

graph_builder.add_node("node1", node1)
graph_builder.add_node("node2", node2)
graph_builder.add_node("node3", node3)
graph_builder.add_node("node4", node4)

graph_builder.add_edge(START, "node1")
graph_builder.add_edge("node1", "node2")
graph_builder.add_edge("node2", "node3")
graph_builder.add_edge("node3", "node4")
graph_builder.add_edge("node4", END)

graph = graph_builder.compile()


initial_state = {"messages": []}

final_state = graph.invoke(initial_state)

print(final_state)