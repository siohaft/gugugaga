import importlib.abc
import importlib.util
import sys
from pathlib import Path

from .translator import translate


class GuguLoader(importlib.abc.Loader):
    def __init__(self, path):
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        source = self.path.read_text(encoding="utf-8")
        python_code = translate(source)

        code = compile(python_code, str(self.path), "exec")

        exec(code, module.__dict__)


class GuguFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        module_path = fullname.replace(".", "/") + ".gugu"

        for search_path in sys.path:
            if not search_path:
                search_path = "."

            candidate = Path(search_path) / module_path

            if candidate.is_file():
                loader = GuguLoader(candidate)

                return importlib.util.spec_from_file_location(
                    fullname, candidate, loader=loader
                )

        return None


def install():
    for finder in sys.meta_path:
        if isinstance(finder, GuguFinder):
            return

    sys.meta_path.insert(0, GuguFinder())
