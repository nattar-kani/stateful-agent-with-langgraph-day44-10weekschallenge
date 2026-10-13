from typing import Literal, TypedDict

class AgentState(TypedDict):
    task: str
    action: Literal["calculate","destructive","final"]
    expression: str
    result: int | float | None
    approval: bool | None
    answer: str | None  