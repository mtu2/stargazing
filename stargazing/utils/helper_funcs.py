import contextlib
import io
from typing import Callable, Iterable, Union


def null_fn() -> None:
    return None


def check_null_fn(fn: Union[Callable[[], None], None]) -> Callable[[], None]:
    if fn is None:
        return null_fn
    return fn

def check_iterable(s: Union[str, Iterable[str]]) -> None:
    if isinstance(s, str):
        return [s]
    return s


class NullIO(io.StringIO):
    def write(self, txt: str) -> None:
       pass
    
def silent_stderr(fn):
    """Decorator to silence stderr output of functions."""
    def silent_fn(*args, **kwargs):
        with contextlib.redirect_stderr(NullIO()):
            return fn(*args, **kwargs)
    return silent_fn
