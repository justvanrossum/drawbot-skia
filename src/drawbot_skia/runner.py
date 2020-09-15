import math
import os
import traceback


def makeNamespace(*objects, **kwargs):
    namespace = kwargs
    for obj in objects:
        for name in dir(obj):
            if not name.startswith("_"):
                namespace[name] = getattr(obj, name)
    return namespace


def runScript(source, sourcePath, namespace=None):
    if namespace is None:
        namespace = {}
    namespace.update({"__name__": "__main__", "__file__": sourcePath})

    if sourcePath:
        parentDir = os.path.dirname(sourcePath)
        saveDir = os.getcwd()
    else:
        parentDir = None
        saveDir = None

    code = compile(source)

    if parentDir is not None:
        os.chdir(parentDir)
    try:
        exec(code, namespace)
    finally:
        if saveDir is not None:
            os.chdir(saveDir)
