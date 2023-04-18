import sys
from contextlib import contextmanager
from typing import Generator


@contextmanager
def contain_imports() -> Generator[None, None, None]:
    """
    Destory modules imported inside the context when leaving it.
    Used to work around "Access is denied" error thrown on Windows when uninstall/updating the add-on.
    """
    existing_modules = sys.modules.copy()
    yield
    for name, mod in sys.modules.items():
        if name not in existing_modules:
            del mod
