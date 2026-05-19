# # Smart Email Support Assistant - Conditional Routing Example

# from langgraph.graph import StateGraph, START, END
# from langchain_openai import ChatOpenAI
# from typing import TypedDict, Literal
# from dotenv import load_dotenv

# load_dotenv(dotenv_path=r"../.env")

# llm = ChatOpenAI(model="gpt-4o-mini")


# # ✅ Shared State
# class SupportState(TypedDict):
#     email_text: str
#     cleaned_text: str
#     category: str
#     response: str
#     summary: str


# # ✅ Step 1: Preprocess Email
# def preprocess_email(state: SupportState):
#     text = state["email_text"].strip().lower()
#     return {"cleaned_text": text}


# # ✅ Step 2: Categorize Email
# def categorize_email(state: SupportState):
#     prompt = f"""
#     You are a support triage assistant.
#     Read this email and classify it as exactly one of the following:
#     - billing
#     - technical
#     - general

#     Email: {state["cleaned_text"]}

#     Respond with only one word: billing, technical, or general.
#     """

#     predicted_category = llm.invoke(prompt).content.strip().lower()

#     # fallback safety
#     if predicted_category not in {"billing", "technical", "general"}:
#         predicted_category = "general"

#     return {"category": predicted_category}


# # ✅ Step 3: Conditional Routing Function
# def route_next(state: SupportState) -> Literal["billing_node", "tech_node", "clarify_node"]:
#     c = state["category"]

#     if "bill" in c:
#         return "billing_node"
#     elif "tech" in c:
#         return "tech_node"
#     else:
#         return "clarify_node"


# # ✅ Step 4: Response Nodes
# def billing_node(state):
#     return {"response": "Your billing issue has been forwarded to our accounts team."}


# def tech_node(state):
#     return {"response": "Our technical team will review your issue shortly."}


# def clarify_node(state):
#     return {"response": "Could you please provide more details about your query?"}


# # ✅ Step 5: Summarize Interaction
# def summarize_interaction(state):
#     summary = llm.invoke(f"""
#     Summarize this support interaction in one sentence:

#     Email: {state["email_text"]}
#     Category: {state["category"]}
#     Response: {state["response"]}
#     """).content

#     return {"summary": summary}


# # ✅ Build Graph
# graph_builder = StateGraph(SupportState)

# graph_builder.add_node("preprocess", preprocess_email)
# graph_builder.add_node("categorize", categorize_email)
# graph_builder.add_node("billing_node", billing_node)
# graph_builder.add_node("tech_node", tech_node)
# graph_builder.add_node("clarify_node", clarify_node)
# graph_builder.add_node("summarize", summarize_interaction)


# # ✅ Flow Definition
# graph_builder.add_edge(START, "preprocess")
# graph_builder.add_edge("preprocess", "categorize")

# # 🔥 Conditional Routing (MAIN FEATURE)
# graph_builder.add_conditional_edges("categorize", route_next)

# graph_builder.add_edge("billing_node", "summarize")
# graph_builder.add_edge("tech_node", "summarize")
# graph_builder.add_edge("clarify_node", "summarize")

# graph_builder.add_edge("summarize", END)


# # ✅ Compile Graph
# graph = graph_builder.compile()


# # ✅ (Optional) Save Graph Diagram
# with open("email_routing.png", "wb") as f:
#     f.write(graph.get_graph().draw_mermaid_png())


# # ✅ Test Emails
# emails = [
#     "I was charged twice on my invoice.",
#     "There's a bug in your app that crashes on login.",
#     "What is your pricing policy?"
# ]


# # ✅ Run for each email
# for email in emails:
#     print("\nInput:", email)

#     final_state = graph.invoke({"email_text": email})

#     print("Response:", final_state["response"])
#     print("Summary:", final_state["summary"])



# Smart Email Support Assistant - Conditional Routing with Label Mapping

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"../.env")

# ✅ Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")


# ✅ Shared State
class SupportState(TypedDict):
    email_text: str
    cleaned_text: str
    category: str
    response: str
    summary: str


# ✅ Step 1: Preprocess Email
def preprocess_email(state: SupportState):
    text = state["email_text"].strip().lower()
    return {"cleaned_text": text}


# ✅ Step 2: Categorize Email
def categorize_email(state: SupportState):
    prompt = f"""
    You are a support triage assistant.
    Read this email and classify it as exactly one of:
    - billing
    - technical
    - general

    Email: {state["cleaned_text"]}

    Respond with only one word: billing, technical, or general.
    """

    predicted_category = llm.invoke(prompt).content.strip().lower()

    # ✅ Fallback safety
    if predicted_category not in {"billing", "technical", "general"}:
        predicted_category = "general"

    return {"category": predicted_category}


# ✅ Step 3: UPDATED Routing Function (returns LABELS, not node names)
def route_next(state: SupportState):
    c = state["category"]

    if "bill" in c:
        return "Billing issue"
    elif "tech" in c:
        return "Technical issue"
    else:
        return "Unclear query"


# ✅ Step 4: Response Nodes
def billing_node(state):
    return {
        "response": "Your billing issue has been forwarded to our accounts team."
    }


def tech_node(state):
    return {
        "response": "Our technical team will review your issue shortly."
    }


def clarify_node(state):
    return {
        "response": "Could you please provide more details about your query?"
    }


# ✅ Step 5: Summarize Interaction
def summarize_interaction(state):
    summary = llm.invoke(f"""
    Summarize this support interaction in one sentence:

    Email: {state["email_text"]}
    Category: {state["category"]}
    Response: {state["response"]}
    """).content

    return {"summary": summary}


# ✅ Build Graph
graph_builder = StateGraph(SupportState)

graph_builder.add_node("preprocess", preprocess_email)
graph_builder.add_node("categorize", categorize_email)
graph_builder.add_node("billing_node", billing_node)
graph_builder.add_node("tech_node", tech_node)
graph_builder.add_node("clarify_node", clarify_node)
graph_builder.add_node("summarize", summarize_interaction)


# ✅ Flow Definition
graph_builder.add_edge(START, "preprocess")
graph_builder.add_edge("preprocess", "categorize")


# 🔥 ✅ UPDATED CONDITIONAL ROUTING (LABEL → NODE MAPPING)
graph_builder.add_conditional_edges(
    "categorize",
    route_next,
    {
        "Billing issue": "billing_node",
        "Technical issue": "tech_node",
        "Unclear query": "clarify_node",
    }
)


# ✅ Merge to summarization
graph_builder.add_edge("billing_node", "summarize")
graph_builder.add_edge("tech_node", "summarize")
graph_builder.add_edge("clarify_node", "summarize")

graph_builder.add_edge("summarize", END)


# ✅ Compile Graph
graph = graph_builder.compile()


# ✅ (Optional) Save diagram
with open("email_routing.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())


# ✅ Test Inputs
emails = [
    "I was charged twice on my invoice.",
    "There's a bug in your app that crashes on login.",
    "What is your pricing policy?"
]


# ✅ Run Workflow
for email in emails:
    print("\nInput:", email)

    final_state = graph.invoke({
        "email_text": email
    })

    print("Response:", final_state["response"])
    print("Summary:", final_state["summary"])