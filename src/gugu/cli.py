import io
import re
import sys
import traceback
from pathlib import Path

from .translator import translate
from .importer import install
from .colors import COLORS

PYTHON_TO_GUGU = {
    # Types
    "int": "guint",
    "float": "gufloat",
    "bool": "gubool",
    "str": "gustr",
    "complex": "gucomplex",
    "bytes": "gubytes",
    "bytearray": "gubytearray",
    "memoryview": "gumemoryview",
    "list": "gulist",
    "tuple": "gutuple",
    "dict": "gudict",
    "set": "guset",
    "frozenset": "gufrozenset",
    # Built-ins
    "print": "gu",
    "input": "gug",
    "min": "gin",
    "max": "gax",
    "open": "guo",
    # Keywords
    "def": "gugu",
    "class": "gugugaga",
    "if": "goo",
    "elif": "goga",
    "else": "gaa",
    "while": "guale",
    "for": "guu",
    "break": "gureak",
    "continue": "gugugoo",
    "True": "goat",
    "False": "gusfand",
    "not": "gunot",
    "and": "guand",
    "or": "guor",
    "in": "ga",
    "as": "go",
    "return": "gaga",
    "from": "gagu",
    "import": "guga",
}


def get_python_exception_text(error):
    buffer = io.StringIO()

    original_stderr = sys.stderr
    sys.stderr = buffer

    try:
        sys.__excepthook__(
            type(error),
            error,
            error.__traceback__,
        )
    finally:
        sys.stderr = original_stderr

    return buffer.getvalue()


def translate_python_suggestions(text):
    def replace(match):
        python_name = match.group(1)

        gugu_name = PYTHON_TO_GUGU.get(
            python_name,
            python_name,
        )

        return f"Did you mean: '{gugu_name}'?"

    return re.sub(
        r"Did you mean: '([^']+)'\?",
        replace,
        text,
    )


def render_gugu_exception(error, path):
    raw = get_python_exception_text(error)

    # Remove Python's ANSI colors because Gugu
    # will apply its own color scheme.
    raw = re.sub(
        r"\x1b\[[0-9;]*m",
        "",
        raw,
    )

    # Convert Python terminology back into Gugu.
    raw = translate_python_suggestions(raw)

    lines = raw.rstrip("\n").splitlines()

    for line in lines:
        stripped = line.strip()

        if stripped == "Traceback (most recent call last):":
            print(
                COLORS.traceback_header(stripped),
                file=sys.stderr,
            )
            continue

        file_match = re.match(
            r'\s*File "(.+)", line (\d+), in (.+)',
            line,
        )

        if file_match:
            filename = file_match.group(1)
            line_number = int(file_match.group(2))
            function_name = file_match.group(3)

            print(
                COLORS.traceback_location(
                    filename,
                    line_number,
                    function_name,
                ),
                file=sys.stderr,
            )
            continue

        # if "Did you mean:" in line:
        #     print(
        #         COLORS.suggestion(stripped),
        #         file=sys.stderr,
        #     )
        #     continue

        # # Final exception:
        # # NameError: ...
        # # TypeError: ...
        # # ValueError: ...
        # # ZeroDivisionError: ...
        # # etc.
        # if not line.startswith(" ") and ":" in line:
        #     exception_name, message = line.split(
        #         ":",
        #         1,
        #     )

        #     print(
        #         COLORS.exception_header(
        #             exception_name,
        #             message.strip(),
        #         ),
        #         file=sys.stderr,
        #     )
        #     continue

        # # Source lines and traceback details
        # print(
        #     COLORS.source_code(line),
        #     file=sys.stderr,
        # )

        if not line.startswith(" ") and ":" in line:
            exception_name, message = line.split(
                ":",
                1,
            )

            print(
                COLORS.exception_header(
                    exception_name,
                    message.strip(),
                ),
                file=sys.stderr,
            )
            continue

        if "Did you mean:" in line:
            print(
                COLORS.suggestion(stripped),
                file=sys.stderr,
            )
            continue


def main():
    if len(sys.argv) != 2:
        print("Usage: gugu <file.gugu>")
        return 1

    path = Path(sys.argv[1]).resolve()

    if path.suffix != ".gugu":
        print("Error: expected a .gugu file")
        return 1

    # Allow imports to find .gugu files next to the current file.
    sys.path.insert(0, str(path.parent))

    # Enable importing .gugu files.
    install()

    source = path.read_text(encoding="utf-8")
    python_code = translate(source)

    # exec(
    #     compile(python_code, str(path), "exec"),
    #     {
    #         "__name__": "__main__",
    #         "__file__": str(path),
    #     },
    # )

    try:
        exec(
            compile(
                python_code,
                str(path),
                "exec",
            ),
            {
                "__name__": "__main__",
                "__file__": str(path),
            },
        )

    except Exception as error:
        render_gugu_exception(
            error,
            path,
        )

        raise SystemExit(1)

    return 0
