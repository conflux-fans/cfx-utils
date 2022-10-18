from importlib.machinery import ModuleSpec
import importlib.util
import sys
import functools
from collections import (
    defaultdict
)
from typing import (
    Any,
    Callable,
    List,
    Dict,
    Optional,
    Sequence,
    Set,
)

_post_import_hooks: Dict[Any, List[Any]] = defaultdict(list)

def execute_module_and_post(exec: Callable, posts: Sequence[Callable]) -> Callable:
    @functools.wraps(exec)
    def wrap(module: ModuleSpec) -> Callable:
        rtn = exec(module)
        for post in posts:
            post(module)
        return rtn
    return wrap

class PostImportFinder:
    def __init__(self) -> None:
        self._skip: Set = set()

    def find_spec(self, fullname: str, package: Optional[str]=None, *args: Sequence) -> Optional[ModuleSpec]:
        # we simply ignore args
        if fullname not in _post_import_hooks:
            return None
        # print(fullname)
        # print(args)
        if fullname in self._skip:
            return None
        self._skip.add(fullname)
    
        spec = importlib.util.find_spec(fullname, package)
        if spec is None:
            return None
        assert spec.loader is not None
        spec.loader.exec_module = execute_module_and_post( # type: ignore
            spec.loader.exec_module, _post_import_hooks[fullname] # type: ignore
        )
        self._skip.remove(fullname)
        # change _post_import_hooks[fullname] to empty to avoid modify the module multiple times
        # _post_import_hooks[fullname] = []
        return spec
    
def when_imported(fullname: str) -> Callable:
    def decorate(func: Callable) -> Callable:
        if fullname in sys.modules:
            func(sys.modules[fullname])
        else:
            _post_import_hooks[fullname].append(func)
        return func
    return decorate

sys.meta_path.insert(0, PostImportFinder()) # type: ignore
