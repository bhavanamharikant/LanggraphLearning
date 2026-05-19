# Looping Workflow to Process a List of Tasks

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


# ✅ Shared State
class State(TypedDict):
    tasks: list[str]


# ✅ Task Processing Node
def task_node(state: State):
    task = state["tasks"][0]
    print(f"Processing task: {task}")

    # Remove processed task (move to next)
    return {"tasks": state["tasks"][1:]}


# ✅ Router for Looping
def should_continue(state: State) -> Literal["loop", "exit"]:
    if state["tasks"]:
        return "loop"   # continue looping
    else:
        return "exit"   # stop loop


# ✅ Build Graph
graph_builder = StateGraph(State)

graph_builder.add_node("task_node", task_node)


# ✅ Conditional Loop
graph_builder.add_conditional_edges(
    "task_node",
    should_continue,
    {
        "loop": "task_node",  # go back (loop)
        "exit": END           # stop
    }
)


# ✅ Start Edge
graph_builder.add_edge(START, "task_node")


# ✅ Compile Graph
graph = graph_builder.compile()


# ✅ (Optional) Graph image
with open("loop_graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())


# ✅ Initial Input
initial_state = {
    "tasks": ["Email client", "Write report", "Schedule meeting"]
}


# ✅ Run Workflow
graph.invoke(initial_state)