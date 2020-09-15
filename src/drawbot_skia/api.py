from .drawbot import Drawbot
from .runner import makeDrawbotNamespace


__all__ = []
_db = Drawbot()
_dbNamespace = makeDrawbotNamespace(_db)
globals().update(_dbNamespace)
__all__.extend(_dbNamespace.keys())
