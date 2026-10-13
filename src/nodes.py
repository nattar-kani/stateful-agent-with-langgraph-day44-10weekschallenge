import json
import ollama

from langgraph.types import interrupt

from src.state import AgentState
from src.tools import calculate, simulate_destructive_action

MODEL = "qwen2.5:1.5b"

def agent_node(state: AgentState) -> dict:
    
    prompt = f"""
You are an assistant in a controlled workflow.

User request: {state['task']}

Choose exactly one action:
- calculate: for arthmetic calculations
- destructive: for a potentially destructive request
- final: when you can answer without another tool

Return only a JSON object with these keys:
action, expression, answer

Rules:
- action must be calculate, destructive, or final.
- expression must be a string. Use an empty string when not needed.
- answer must be a string. Use an empty string when not needed.
- Never claim that a destructive action has already been executed.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        format="json",
        options={"temperature":0}
    )

    content = response["message"]["content"]

    if not content:
        raise ValueError("The LLM returned an empty response")

    try:
        decision = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError("The LLM returned invalid JSON") from e

    if not isinstance(decision,dict):
        raise ValueError("The LLM response must be a JSON object")

    if set(decision) != {"action","expression","answer"}:
        raise ValueError("Unexpected keys in the LLM response")

    action = decision["action"]
    expression = decision["expression"]
    answer = decision["answer"]

    if action not in {"calculate", "destructive", "final"}:
        raise ValueError(f"Unsupported action: {action!r}")

    if not isinstance(expression, str) or not isinstance(answer, str):
        raise ValueError("Expression and answer must be strings")

    if action == "calculate" and not expression.strip():
        raise ValueError("A calculation requires an expression")

    if action == "final" and not answer.strip():
        raise ValueError("A final action requires an answer")

    return {
        "action": action,
        "expression": expression,
        "answer": answer if action == "final" else None,
    }

def calculator_node(state: AgentState)->dict:
    result = calculate(state["expression"])

    return {
        "result": float(result) if "." in result else int(result)
    }

def approval_node(state:AgentState)->dict:
    decision = interrupt({
        "message": "Human approval is required before the simulated action",
        "requested_action": state["task"],
        "warning": "Simulation only. No real files will be changed"
    })

    if not isinstance(decision,bool):
        raise ValueError("Approval response must be True or False")

    return {"approval": decision}

def destructive_action_node(state: AgentState) -> dict:

    if state["approval"] is not True:
        raise PermissionError("Action requires explicit human approval")

    return {
        "answer": simulate_destructive_action(state["approval"]),
    }


def final_node(state: AgentState) -> dict:
    if state["answer"]:
        return {}

    if state["result"] is not None:
        return {
            "answer": f"The calculation result is {state['result']}."
        }

    return {
        "answer": "The request was not executed."
    }
