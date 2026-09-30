from .lexer import translate_line
from .parser import validate


def translate(source):
    validate(source)

    lines = []

    for line in source.splitlines():
        stripped = line.lstrip()

        if stripped.startswith("gua "):
            indentation = line[: len(line) - len(stripped)]
            stripped = stripped[4:]
            line = indentation + stripped

        lines.append(translate_line(line))

    return "\n".join(lines)
