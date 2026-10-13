
from src.agent import route_agent, route_approval


def test_route_agent_to_calculator():
    state = {"action": "calculate"}
    assert route_agent(state) == "calculator"


def test_route_agent_to_approval():
    state = {"action": "destructive"}
    assert route_agent(state) == "approval"


def test_route_agent_to_final():
    state = {"action": "final"}
    assert route_agent(state) == "final"


def test_approved_action_can_proceed():
    state = {"approval": True}
    assert route_approval(state) == "destructive_action"


def test_rejected_action_skips_execution():
    state = {"approval": False}
    assert route_approval(state) == "final"


def test_missing_approval_skips_execution():
    state = {"approval": None}
    assert route_approval(state) == "final"
