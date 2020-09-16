import argparse
import sys
from .drawbot import Drawbot
from .runner import makeDrawbotNamespace, runScriptSource


def main(args=None):
    if args is None:
        args = sys.argv

    parser = argparse.ArgumentParser(
        prog="drawbot",
        description="Command line DrawBot tool.",
    )
    parser.add_argument("drawbot_script", type=argparse.FileType("r"))
    parser.add_argument("output_file", nargs="*", default=[])

    args = parser.parse_args()
    db = Drawbot()
    namespace = makeDrawbotNamespace(db)
    runScriptSource(args.drawbot_script.read(), args.drawbot_script.name, namespace)
    for path in args.output_file:
        db.saveImage(path)


if __name__ == "__main__":
    main()
