def calculate(expression: str) -> str:
    import ast
    import operator

    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            left = evaluate(node.left)
            right = evaluate(node.right)
            return operators[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value

        raise ValueError("Unsupported arithmetic expression")

    if len(expression) > 100:
        raise ValueError("Expression is too long")

    tree = ast.parse(expression, mode="eval")
    result = evaluate(tree.body)

    return str(result)


TOOLS = {
    "calculate": calculate,
}

def simulate_destructive_action(approval: bool | None) -> str:
    if approval is not True:
        raise PermissionError("Action required explicit human approval")
    return "SIMULATION ONLY: Destructive action approved and simulated. No files were changed"

def execute_tool(tool_name: str, arguments: dict) -> str:
    tool = TOOLS.get(tool_name)

    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary")

    if tool_name == "calculate":
        if set(arguments) != {"expression"}:
            raise ValueError("Expected only the 'expression' argument")

        if not isinstance(arguments["expression"], str):
            raise ValueError("'expression' must be a string")

        return tool(arguments["expression"])

    raise ValueError("Tool execution is not configured")
