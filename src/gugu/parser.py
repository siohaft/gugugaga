import ast
import builtins
import re


class GuguSyntaxError(SyntaxError):
    pass


FORBIDDEN_BUILTINS = set(dir(builtins)) - {"range"}


GUGU_KEYWORDS = {
    "gugugaga",
    "gugu",
    "goo",
    "goga",
    "gaa",
    "guale",
    "guu",
    "gureak",
    "gugugoo",
    "ga",
    "go",
    "gunot",
    "guand",
    "guor",
    "goat",
    "gusfand",
    "gu",
    "gug",
    "gin",
    "gax",
    "guo",
    "gaga",
    "gagu",
    "guga",
    "gua",
    # Decorators
    "gugustatic",
    "guguclass",
    "guguproperty",
    # Data types
    "guint",
    "gufloat",
    "gudouble",
    "gucomplex",
    "gubool",
    "gustr",
    "gubytes",
    "gubytearray",
    "gumemoryview",
    "gulist",
    "gutuple",
    "gudict",
    "guset",
    "gufrozenset",
}


GUGU_CALLABLES = {
    "gu",
    "gug",
    "gin",
    "gax",
    "guo",
    # Data types
    "guint",
    "gufloat",
    "gudouble",
    "gucomplex",
    "gubool",
    "gustr",
    "gubytes",
    "gubytearray",
    "gumemoryview",
    "gulist",
    "gutuple",
    "gudict",
    "guset",
    "gufrozenset",
}


EXPRESSION_KEYWORDS = {
    "ga": "in",
    "gunot": "not",
    "guand": "and",
    "guor": "or",
    "goat": "True",
    "gusfand": "False",
}


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
    ast.Not,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.Slice,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Set,
    ast.JoinedStr,
    ast.FormattedValue,
    ast.keyword,
}


CLASS_RE = re.compile(r"^gugugaga\s+([A-Za-z_]\w*)\s*:$")

DEF_RE = re.compile(r"^gugu\s+([A-Za-z_]\w*)\s*" r"\((.*?)\)\s*:$")

DECORATOR_RE = re.compile(r"^@(gugustatic|guguclass|guguproperty)$")

IF_RE = re.compile(r"^goo\s+(.+)\s*:$")

ELIF_RE = re.compile(r"^goga\s+(.+)\s*:$")

ELSE_RE = re.compile(r"^gaa\s*:$")

WHILE_RE = re.compile(r"^guale\s+(.+)\s*:$")

FOR_RE = re.compile(r"^guu\s+([A-Za-z_]\w*)\s+ga\s+(.+)\s*:$")

BREAK_RE = re.compile(r"^gureak$")

CONTINUE_RE = re.compile(r"^gugugoo$")

PRINT_RE = re.compile(r"^gu\((.*)\)$")

RETURN_RE = re.compile(r"^gaga(?:\s+(.+))?$")

MODULE_IMPORT_RE = re.compile(r"^guga\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)$")

IMPORT_RE = re.compile(
    r"^gagu\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
    r"\s+guga\s+(\*|[A-Za-z_]\w*)"
    r"(?:\s+go\s+([A-Za-z_]\w*))?$"
)

VAR_RE = re.compile(r"^gua\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)" r"\s*=\s*(.+)$")

AUG_ASSIGN_RE = re.compile(
    r"^([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|\[[^\]]+\])*)\s*"
    r"(\+=|-=|\*=|/=|//=|%=|\*\*=|&=|\|=|\^=|>>=|<<=|@=)\s*"
    r"(.+)$"
)

CALL_RE = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*\(.*\)$")


def _error(line_number, message):
    raise GuguSyntaxError(f"Line {line_number}: {message}")


def _strip_comment(line):
    in_string = False
    quote = None
    escaped = False

    for char in line:
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
            if char in ("'", '"'):
                in_string = True
                quote = char

            elif char == "#":
                return line[: line.index(char)].rstrip()

    return line.rstrip()


def _translate_expression_keywords(expression):
    result = []
    word = []
    in_string = False
    quote = None
    escaped = False

    def flush_word():
        if not word:
            return

        text = "".join(word)

        if not in_string:
            result.append(EXPRESSION_KEYWORDS.get(text, text))
        else:
            result.append(text)

        word.clear()

    for char in expression:
        if in_string:
            if escaped:
                result.append(char)
                escaped = False
                continue

            if char == "\\":
                result.append(char)
                escaped = True
                continue

            if char == quote:
                result.append(char)
                in_string = False
                quote = None
            else:
                result.append(char)

        else:
            if char in ("'", '"'):
                flush_word()
                result.append(char)
                in_string = True
                quote = char

            elif char.isalnum() or char == "_":
                word.append(char)

            else:
                flush_word()
                result.append(char)

    flush_word()

    return "".join(result)


def _validate_parameters(parameters, line_number):
    parameters = parameters.strip()

    if not parameters:
        return

    parts = parameters.split(",")

    for part in parts:
        name = part.strip()

        if not re.fullmatch(r"[A-Za-z_]\w*", name):
            _error(line_number, f"Invalid parameter name '{name}'.")

        if name in GUGU_KEYWORDS:
            _error(line_number, f"'{name}' is a reserved Gugu keyword.")


def _validate_expression(expression, line_number):
    expression = expression.strip()

    if not expression:
        _error(line_number, "Expected an expression.")

    expression = _translate_expression_keywords(expression)

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        _error(line_number, f"Invalid Gugu expression: {expression!r}")

    for node in ast.walk(tree):
        if type(node) not in ALLOWED_EXPRESSION_NODES:
            _error(line_number, f"'{type(node).__name__}' is not valid Gugu syntax.")

        if isinstance(node, ast.Constant):
            if node.value is None:
                _error(line_number, "None is not valid Gugu syntax.")

        if isinstance(node, ast.Name):
            if node.id in GUGU_KEYWORDS:
                is_function = any(
                    isinstance(parent, ast.Call) and parent.func is node
                    for parent in ast.walk(tree)
                )

                if node.id not in GUGU_CALLABLES or not is_function:
                    _error(line_number, f"'{node.id}' is a reserved Gugu keyword.")

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                function_name = node.func.id

                if function_name in FORBIDDEN_BUILTINS:
                    _error(line_number, f"'{function_name}()' is not a Gugu function.")


def _validate_assignment_target(target, line_number):
    try:
        tree = ast.parse(target, mode="eval")
    except SyntaxError:
        _error(line_number, f"Invalid assignment target: {target!r}")

    if not isinstance(tree.body, (ast.Name, ast.Attribute, ast.Subscript)):
        _error(line_number, f"'{target}' is not a valid assignment target.")

    if isinstance(tree.body, ast.Name):
        if tree.body.id in GUGU_KEYWORDS:
            _error(line_number, f"'{tree.body.id}' is a reserved Gugu keyword.")


def _parse_statement(code, line_number):
    match = CLASS_RE.fullmatch(code)
    if match:
        class_name = match.group(1)

        if class_name in GUGU_KEYWORDS:
            _error(line_number, f"'{class_name}' is a reserved Gugu keyword.")

        return "class", True

    match = DEF_RE.fullmatch(code)
    if match:
        function_name = match.group(1)

        if function_name in GUGU_KEYWORDS:
            _error(line_number, f"'{function_name}' is a reserved Gugu keyword.")

        _validate_parameters(match.group(2), line_number)

        return "def", True

    match = DECORATOR_RE.fullmatch(code)
    if match:
        return "decorator", False

    match = IF_RE.fullmatch(code)
    if match:
        _validate_expression(match.group(1), line_number)

        return "if", True

    match = ELIF_RE.fullmatch(code)
    if match:
        _validate_expression(match.group(1), line_number)

        return "elif", True

    match = ELSE_RE.fullmatch(code)
    if match:
        return "else", True

    match = WHILE_RE.fullmatch(code)
    if match:
        _validate_expression(match.group(1), line_number)

        return "while", True

    match = FOR_RE.fullmatch(code)
    if match:
        variable_name = match.group(1)

        if variable_name in GUGU_KEYWORDS:
            _error(line_number, f"'{variable_name}' is a reserved Gugu keyword.")

        _validate_expression(match.group(2), line_number)

        return "for", True

    match = BREAK_RE.fullmatch(code)
    if match:
        return "break", False

    match = CONTINUE_RE.fullmatch(code)
    if match:
        return "continue", False

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

    match = MODULE_IMPORT_RE.fullmatch(code)
    if match:
        return "module_import", False

    match = IMPORT_RE.fullmatch(code)
    if match:
        imported_name = match.group(2)
        alias = match.group(3)

        if imported_name != "*":
            if imported_name in GUGU_KEYWORDS:
                _error(line_number, f"'{imported_name}' is a reserved Gugu keyword.")

        if alias and alias in GUGU_KEYWORDS:
            _error(line_number, f"'{alias}' is a reserved Gugu keyword.")

        return "import", False

    match = VAR_RE.fullmatch(code)
    if match:
        variable_names = [name.strip() for name in match.group(1).split(",")]

        expression = match.group(2)

        for variable_name in variable_names:
            if variable_name in GUGU_KEYWORDS:
                _error(line_number, f"'{variable_name}' is a reserved Gugu keyword.")

        _validate_expression(expression, line_number)

        return "var", False

    match = AUG_ASSIGN_RE.fullmatch(code)
    if match:
        target = match.group(1)
        expression = match.group(3)

        _validate_assignment_target(target, line_number)

        _validate_expression(expression, line_number)

        return "aug_assign", False

    if CALL_RE.fullmatch(code):
        _validate_expression(code, line_number)

        return "call", False

    _error(line_number, f"'{code}' is not valid Gugu syntax.")


def validate(source):
    indentation_stack = [0]
    last_statement_at_indent = {}

    previous_indent = 0
    expecting_indented_block = False
    pending_decorator = False

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

        if pending_decorator:
            if statement_type == "decorator":
                pass
            elif statement_type == "def":
                pending_decorator = False
            else:
                _error(line_number, "A Gugu decorator must be followed by a function.")

        if statement_type == "decorator":
            pending_decorator = True

        if statement_type == "elif":
            if last_statement_at_indent.get(indentation) not in {
                "if",
                "elif",
            }:
                _error(
                    line_number, "'goga' must directly follow a 'goo' or 'goga' block."
                )

        if statement_type == "else":
            if last_statement_at_indent.get(indentation) not in {
                "if",
                "elif",
            }:
                _error(
                    line_number, "'gaa' must directly follow a 'goo' or 'goga' block."
                )

        last_statement_at_indent[indentation] = statement_type

        if opens_block:
            expecting_indented_block = True

        previous_indent = indentation

    if expecting_indented_block:
        _error(line_number, "A block must contain at least one indented line.")

    if pending_decorator:
        _error(line_number, "A decorator must be followed by a function.")
