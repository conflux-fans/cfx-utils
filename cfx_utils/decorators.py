from typing import Any, Callable, Dict, Generic, Type, TypeVar
import functools

T = TypeVar("T")
R = TypeVar("R")

class combomethod(Generic[R], object):
    def __init__(self, method: Callable[..., R]) -> None:
        self.method = method

    def __get__(self, obj: T = None, objtype: Type[T] = None) -> Callable[..., R]:
        @functools.wraps(self.method)
        def _wrapper(*args: Any, **kwargs: Any) -> R:
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)

        return _wrapper
