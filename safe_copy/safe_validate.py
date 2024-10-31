import argparse
import pathlib
import sys


def safe_validate(directory):
    assert directory.is_dir()

    print(f"Validating {directory}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Tool to validate a directory that has been copied via safe-copy, this"
                                                 "is useful for later data integrity")
    parser.add_argument("--directory", required=True, help="The directory to validate")

    args = parser.parse_args()

    sys.exit(safe_validate(pathlib.Path(args.directory)))