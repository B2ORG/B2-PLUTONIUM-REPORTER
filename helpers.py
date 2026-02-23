from functools import wraps
from inspect import signature
from pathlib import Path


def file_io(fn):
    @wraps(fn)
    def _wrap(*args, **kwargs):
        paths: list[Path] = [f"'{p}'" for p in [*args, *list(kwargs.values()), *list(kwargs.keys())] if isinstance(p, Path)]
        assert len(paths), "Decorator file_io should only decorate functions that take in Path argument"

        try:
            fn(*args, **kwargs)
        except (PermissionError, FileNotFoundError, FileExistsError):
            print(f"FileIO encountered an error in function {fn.__qualname__}{signature(fn)}, with paths: {", ".join(paths)}")
            raise

    return _wrap
