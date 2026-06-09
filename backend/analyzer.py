import ast


def analyze_code(code_text: str, filename: str) -> dict:
    alerts = []
    function_lengths = []
    categories = {"Length": 0, "Docstring": 0, "Unused": 0, "Hebrew": 0, "Syntax": 0}

    lines = code_text.splitlines()
    if len(lines) > 200:
        alerts.append(f"File '{filename}' is too long ({len(lines)} lines). Max is 200.")
        categories["Length"] += 1

    try:
        tree = ast.parse(code_text)
    except SyntaxError as e:
        alerts.append(f"Syntax error in '{filename}' at line {e.lineno}: {e.msg}")
        categories["Syntax"] += 1
        return {"alerts": alerts, "function_lengths": [], "categories": categories}

    def contains_hebrew(text):
        return any('֐' <= char <= '׿' for char in text)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            length = end - start + 1
            function_lengths.append(length)

            if length > 20:
                alerts.append(f"Function '{node.name}' in '{filename}' is too long ({length} lines).")
                categories["Length"] += 1

            if ast.get_docstring(node) is None:
                alerts.append(f"Missing docstring in function '{node.name}' in '{filename}' at line {node.lineno}.")
                categories["Docstring"] += 1

            if contains_hebrew(node.name):
                alerts.append(f"Hebrew function name warning: '{node.name}' in '{filename}' at line {node.lineno}.")
                categories["Hebrew"] += 1

            defined_vars = {}
            used_vars = set()
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Assign):
                    for target in sub_node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars[target.id] = target.lineno
                            if contains_hebrew(target.id):
                                alerts.append(
                                    f"Hebrew variable name warning: '{target.id}' in '{filename}' at line {target.lineno}.")
                                categories["Hebrew"] += 1
                if isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Load):
                    used_vars.add(sub_node.id)

            for var_name, line_no in defined_vars.items():
                if var_name not in used_vars:
                    alerts.append(
                        f"Unused variable warning: '{var_name}' in '{filename}' at line {line_no} is defined but never used.")
                    categories["Unused"] += 1

    return {
        "alerts": list(set(alerts)),
        "function_lengths": function_lengths,
        "categories": categories
    }
