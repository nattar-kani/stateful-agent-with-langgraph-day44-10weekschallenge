# Day 44 — Building a Stateful AI Agent with LangGraph

Part of my **70 Days / 10 Week AI Engineer Challenge**.

On Day 43, I built a ReAct agent with a manually controlled reasoning and tool-execution loop. Today, I rebuilt the workflow using LangGraph to understand how stateful agent workflows can be represented as graphs.

## What I Built

A stateful AI agent that uses a local Ollama model to choose between three actions:

- **Calculate:** Execute a supported arithmetic expression.
- **Destructive:** Request human approval before running a simulated destructive action.
- **Final:** Return a response without calling another tool.

LangGraph manages the workflow transitions, while the application validates the model's response and controls tool execution.

## Tech Stack

- Python
- LangGraph
- Ollama
- `qwen2.5:1.5b`
- Pytest

The model runs locally through Ollama, so the workflow does not require an external LLM API.

## Architecture

```text
START
  |
  v
Agent Node (Ollama)
  |
  v
Conditional Routing
  |
  +---- calculate ----> Calculator
  |                       |
  |                       v
  |                    Agent Node
  |
  +---- destructive --> Approval Node
  |                       |
  |                  Human Decision
  |                    /       \
  |              Approved    Rejected
  |                  |           |
  |                  v           |
  |           Simulated Action   |
  |                  |           |
  +---- final -------+-----------+
                     |
                     v
                 Final Node
                     |
                     v
                    END
```

## Key Concepts Learned

### 1. State

The `AgentState` TypedDict defines the shared information used by the workflow, including the user's task, selected action, arithmetic expression, result, approval decision, and final answer.

Nodes return dictionaries containing state updates. LangGraph uses these updates to maintain the workflow's state as execution progresses.

### 2. Nodes and Edges

Nodes are Python functions responsible for individual operations. Edges define the transitions between them.

The graph uses fixed edges for predictable transitions and conditional edges when the next step depends on the agent's decision or the human's approval.

### 3. Conditional Routing

The `route_agent()` function directs the workflow to the calculator, approval, or final node based on the selected action.

The `route_approval()` function allows the workflow to continue to the simulated destructive action only when approval is explicitly `True`.

### 4. Cycles

After the calculator executes, control returns to the agent node. This creates a cycle that allows the agent to inspect the updated state and decide what to do next.

Unlike the manual loop from Day 43, this cycle is represented explicitly in the graph.

### 5. Checkpointing

The graph uses LangGraph's `InMemorySaver` checkpointer to preserve workflow checkpoints during execution.

A `thread_id` identifies the workflow thread, allowing an interrupted workflow to resume with its saved state.

This implementation is intended for local experimentation. In-memory checkpoints do not persist after the process ends.

### 6. Human-in-the-Loop

The approval node uses LangGraph's `interrupt()` mechanism to pause execution and request a human decision.

The workflow resumes using `Command(resume=...)` with the same thread configuration.

- If approved, the graph runs the simulated action.
- If rejected, the graph skips the action and proceeds to the final node.

**Safety boundary:** Destructive operations are simulated only. No files are deleted. The action node independently checks that approval is explicitly `True`, rather than relying solely on the LLM or routing logic.

### 7. Structured LLM Output

The agent prompt asks Ollama to return a JSON object containing `action`, `expression`, and `answer`.

The application parses the response and validates the expected keys, supported actions, and field types before using the decision for routing.

Prompt instructions help guide the model, but validation and execution safeguards are enforced by the application.

## Project Structure

```text
Day 44/
├── src/
│   ├── __init__.py
│   ├── state.py
│   ├── tools.py
│   ├── nodes.py
│   └── agent.py
├── tests/
│   └── test_graph.py
├── main.py
├── requirements.txt
└── README.md
```

## Setup and Run

### Prerequisites

- Python installed
- Ollama installed and running
- The `qwen2.5:1.5b` model available locally

Pull the model if it is not already installed:

```bash
ollama pull qwen2.5:1.5b
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

When a potentially destructive request triggers the approval node, enter `yes` to approve the simulation or `no` to reject it.

### Run Tests

```bash
python -m pytest tests/test_graph.py -v
```

The routing tests verify the selected destination for each supported action and ensure that only explicit approval can reach the simulated destructive-action node.

---