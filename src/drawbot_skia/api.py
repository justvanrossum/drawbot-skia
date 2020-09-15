from math import *
import math
from .drawbot import Drawbot
from .path import Path

_db = Drawbot()

__all__ = []

_namespace = globals()

for _name in dir(math):
    if not _name.startswith("_"):
        __all__.append(_name)


for _name in dir(_db):
    if not _name.startswith("_"):
        __all__.append(_name)
        _namespace[_name] = getattr(_db, _name)

__all__.append("Path")
