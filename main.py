from langgraph.types import Command

from src.agent import app


def main():
    task = "Delete the old project files"

    config = {"configurable": {"thread_id": "day44-demo-1"}}

    initial_state = {
        "task": task,
        "action": "final",
        "expression": "",
        "result": None,
        "approval": None,
        "answer": None,
    }

    print(f"Task: {task}\n")

    result = app.invoke(initial_state, config=config)

    if result.get("__interrupt__"):
        interrupt_info = result["__interrupt__"][0].value

        print("HUMAN APPROVAL REQUIRED")
        print(interrupt_info["message"])
        print(f"Requested action: {interrupt_info['requested_action']}")
        print(interrupt_info["warning"])

        response = input("\nApprove simulation? (yes/no): ").strip().lower()
        approved = response == "yes"

        result = app.invoke(
            Command(resume=approved),
            config=config,
        )

    print("\nFinal answer:")
    print(result.get("answer", "No answer was produced."))


if __name__ == "__main__":
    main()
