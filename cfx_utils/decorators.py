from typing import (
    Any,
    Callable,
    TypeVar,
    Generic,
    Union,
)
from typing_extensions import (
    ParamSpec,
    Concatenate
)
import functools

R = TypeVar("R") # return value
P = ParamSpec("P")

class combomethod(Generic[P, R], object):
    def __init__(self, method: Callable[Concatenate[Any, P], R]) -> None:
        self.method = method

    def __get__(
        self, obj: object = None, objtype: Union[type, None] = None
    ) -> Callable[P, R]:
        @functools.wraps(self.method)
        def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if obj is not None:
                # classmethod
                return self.method(obj, *args, **kwargs)
            else:
                # not a classmethod
                return self.method(objtype, *args, **kwargs)

        return _wrapper

