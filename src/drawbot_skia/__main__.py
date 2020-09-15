import argparse
import sys


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
    print(args.drawbot_script)
    print(args.output_file)


if __name__ == "__main__":
    main()
