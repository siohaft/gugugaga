import sys
from pathlib import Path

from .translator import translate
from .importer import install


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

    exec(
        compile(python_code, str(path), "exec"),
        {
            "__name__": "__main__",
            "__file__": str(path),
        },
    )

    return 0
