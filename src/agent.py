import json
import ollama

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END,START,StateGraph

from src.nodes import (
    agent_node,
    approval_node,
    calculator_node,
    destructive_action_node,
    final_node
)
from src.state import AgentState

def route_agent(state:AgentState)->str:
    action = state["action"]

    if action == "calculate":
        return "calculator"

    if action == "destructive":
        return "approval"

    if action == "final":
        return "final"

    raise ValueError(f"Unsupported action: {action!r}")

def route_approval(state: AgentState) -> str:

    if state["approval"] is True:
        return "destructive_action"
    return "final"

def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("agent",agent_node)
    graph.add_node("calculator",calculator_node)
    graph.add_node("approval",approval_node)
    graph.add_node("destructive_action",destructive_action_node)
    graph.add_node("final",final_node)

    graph.add_edge(START,"agent")

    graph.add_conditional_edges(
        "agent",
        route_agent,
        {
            "calculator":"calculator",
            "approval":"approval",
            "final":"final"
        }
    )

    graph.add_edge("calculator","agent")

    graph.add_conditional_edges(
        "approval",
        route_approval,
        {
            "destructive_action":"destructive_action",
            "final":"final"
        }
    )

    graph.add_edge("destructive_action","final")
    graph.add_edge("final",END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)

app = build_agent()
