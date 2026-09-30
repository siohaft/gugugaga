import ast
import builtins
import re


class GuguSyntaxError(SyntaxError):
    pass


FORBIDDEN_BUILTINS = set(dir(builtins)) - {"range"}


ALLOWED_EXPRESSION_NODES = {
    ast.Expression,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.Slice,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Set,
    ast.keyword,
}


CLASS_RE = re.compile(r"^gugugaga\s+([A-Za-z_]\w*)\s*:$")

DEF_RE = re.compile(r"^gugu\s+([A-Za-z_]\w*)\s*" r"\((.*?)\)\s*:$")

IF_RE = re.compile(r"^goo\s+(.+)\s*:$")

ELSE_RE = re.compile(r"^gaa\s*:$")

FOR_RE = re.compile(r"^guu\s+([A-Za-z_]\w*)\s+ga\s+(.+)\s*:$")

PRINT_RE = re.compile(r"^gu\((.*)\)$")

RETURN_RE = re.compile(r"^gaga(?:\s+(.+))?$")

IMPORT_RE = re.compile(
    r"^gagu\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
    r"\s+guga\s+([A-Za-z_]\w*)"
    r"(?:\s+go\s+([A-Za-z_]\w*))?$"
)

VAR_RE = re.compile(r"^gua\s+([A-Za-z_]\w*)\s*=\s*(.+)$")

CALL_RE = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*\(.*\)$")


def _error(line_number, message):
    raise GuguSyntaxError(f"Line {line_number}: {message}")


def _strip_comment(line):
    in_string = False
    quote = None
    escaped = False

    for i, char in enumerate(line):
        if in_string:
            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == quote:
                in_string = False
                quote = None

        else:
            if char in ('"', "'"):
                in_string = True
                quote = char

            elif char == "#":
                return line[:i].rstrip()

    return line.rstrip()


def _validate_parameters(parameters, line_number):
    parameters = parameters.strip()

    if not parameters:
        return

    parts = parameters.split(",")

    for part in parts:
        name = part.strip()

        if not re.fullmatch(r"[A-Za-z_]\w*", name):
            _error(line_number, f"Invalid parameter name '{name}'.")


def _validate_expression(expression, line_number):
    expression = expression.strip()

    if not expression:
        _error(line_number, "Expected an expression.")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        _error(line_number, f"Invalid Gugu expression: {expression!r}")

    for node in ast.walk(tree):
        if type(node) not in ALLOWED_EXPRESSION_NODES:
            _error(line_number, f"'{type(node).__name__}' is not valid Gugu syntax.")

        if isinstance(node, ast.Constant):
            if node.value is None or isinstance(node.value, bool):
                _error(line_number, f"{node.value!r} is not valid Gugu syntax.")

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                function_name = node.func.id

                if function_name in FORBIDDEN_BUILTINS:
                    _error(line_number, f"'{function_name}()' is not a Gugu function.")


def _parse_statement(code, line_number):
    match = CLASS_RE.fullmatch(code)
    if match:
        return "class", True

    match = DEF_RE.fullmatch(code)
    if match:
        _validate_parameters(match.group(2), line_number)
        return "def", True

    match = IF_RE.fullmatch(code)
    if match:
        _validate_expression(match.group(1), line_number)
        return "if", True

    match = ELSE_RE.fullmatch(code)
    if match:
        return "else", True

    match = FOR_RE.fullmatch(code)
    if match:
        _validate_expression(match.group(2), line_number)
        return "for", True

    match = PRINT_RE.fullmatch(code)
    if match:
        _validate_expression(match.group(1), line_number)
        return "print", False

    match = RETURN_RE.fullmatch(code)
    if match:
        expression = match.group(1)

        if expression:
            _validate_expression(expression, line_number)

        return "return", False

    match = IMPORT_RE.fullmatch(code)
    if match:
        return "import", False

    match = VAR_RE.fullmatch(code)
    if match:
        variable_name = match.group(1)
        expression = match.group(2)

        if variable_name in {
            "gugugaga",
            "gugu",
            "goo",
            "gaa",
            "guu",
            "ga",
            "go",
            "gu",
            "gug",
            "gaga",
            "gagu",
            "guga",
            "gua",
        }:
            _error(line_number, f"'{variable_name}' is a reserved Gugu keyword.")

        _validate_expression(expression, line_number)

        return "var", False

    if CALL_RE.fullmatch(code):
        _validate_expression(code, line_number)
        return "call", False

    _error(line_number, f"'{code}' is not valid Gugu syntax.")


def validate(source):
    indentation_stack = [0]
    last_statement_at_indent = {}

    previous_indent = 0
    expecting_indented_block = False

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        if "\t" in raw_line:
            _error(line_number, "Tabs are not allowed for indentation. Use spaces.")

        code_line = _strip_comment(raw_line)

        if not code_line.strip():
            continue

        indentation = len(code_line) - len(code_line.lstrip(" "))

        code = code_line.strip()

        if expecting_indented_block:
            if indentation <= previous_indent:
                _error(line_number, "Expected an indented block.")

            if indentation != previous_indent + 4:
                _error(line_number, "Gugu blocks must be indented by exactly 4 spaces.")

            indentation_stack.append(indentation)
            expecting_indented_block = False

        elif indentation > previous_indent:
            _error(line_number, "Unexpected indentation.")

        while len(indentation_stack) > 1 and indentation_stack[-1] > indentation:
            indentation_stack.pop()

        if indentation_stack[-1] != indentation:
            _error(line_number, "Invalid indentation level.")

        statement_type, opens_block = _parse_statement(code, line_number)

        if statement_type == "else":
            if last_statement_at_indent.get(indentation) != "if":
                _error(line_number, "'gaa' must directly follow a 'goo' block.")

        last_statement_at_indent[indentation] = statement_type

        if opens_block:
            expecting_indented_block = True

        previous_indent = indentation

    if expecting_indented_block:
        _error(line_number, "A block must contain at least one indented line.")
