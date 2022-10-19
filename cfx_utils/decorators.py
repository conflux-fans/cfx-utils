from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Type,
    TypeVar,
)
from typing_extensions import (
    ParamSpec,
)
import functools

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")

if TYPE_CHECKING:

    def combomethod(method: Callable[P, R]) -> Callable[P, R]:
        ...

else:

    class combomethod(object):
        def __init__(self, method: Callable) -> None:
            self.method = method

        def __get__(self, obj: T = None, objtype: Type[T] = None) -> Callable:
            @functools.wraps(self.method)
            def _wrapper(*args: Any, **kwargs: Any) -> Any:
                if obj is not None:
                    return self.method(obj, *args, **kwargs)
                else:
                    return self.method(objtype, *args, **kwargs)

            return _wrapper
