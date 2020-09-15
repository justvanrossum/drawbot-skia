import math
from .drawbot import Drawbot
from .path import Path  # noqa: F401
from .runner import makeNamespace


__all__ = []
_db = Drawbot()
_dbNamespace = makeNamespace(math, _db, Path=Path)
globals().update(_dbNamespace)
__all__.extend(_dbNamespace.keys())
