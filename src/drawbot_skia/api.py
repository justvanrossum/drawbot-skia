from math import *  # noqa: F401, F403
import math
from .drawbot import Drawbot
from .path import Path  # noqa: F401


__all__ = []


_namespace = globals()
_db = Drawbot()

for _name in dir(math):
    if not _name.startswith("_"):
        __all__.append(_name)

for _name in dir(_db):
    if not _name.startswith("_"):
        __all__.append(_name)
        _namespace[_name] = getattr(_db, _name)

__all__.append("Path")
