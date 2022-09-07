import importlib.util
import sys
import functools
from collections import (
    defaultdict
)
from typing import (
    Any, List
)

_post_import_hooks = defaultdict(list)

def execute_module_and_post(exec, posts):
    @functools.wraps(exec)
    def wrap(module):
        rtn = exec(module)
        for post in posts:
            post(module)
        return rtn
    return wrap

class PostImportFinder:
    def __init__(self):
        self._skip = set()

    def find_spec(self, fullname, package=None, *args):
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
        spec.loader.exec_module = execute_module_and_post(
            spec.loader.exec_module, _post_import_hooks[fullname]
        )
        self._skip.remove(fullname)
        return spec
    
def when_imported(fullname):
    def decorate(func):
        if fullname in sys.modules:
            func(sys.modules[fullname])
        else:
            _post_import_hooks[fullname].append(func)
        return func
    return decorate

sys.meta_path.insert(0, PostImportFinder()) # type: ignore
