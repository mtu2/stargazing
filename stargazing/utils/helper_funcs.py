from typing import Callable, Union


def null_fn() -> None:
    return None


def check_null_fn(fn: Union[Callable[[], None], None]) -> Callable[[], None]:
    if fn is None:
        return null_fn
    return fn
