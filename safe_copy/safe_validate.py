import argparse
import pathlib
from safe_copy.managed_directory import ManagedDirectory
import sys


def safe_validate(directory):
    assert directory.is_dir()

    print(f"Validating {directory}")

    test_directory = ManagedDirectory(directory)
    result = test_directory.validate_checksums()
    if result == 0:
        print("SUCCESS: All files on disk match saved matched")
    else:
        print(f"WARNING: {result} computed checksums did not match")
    return result


def main():
    parser = argparse.ArgumentParser(description="Tool to validate a directory that has been copied via safe-copy, this"
                                                 "is useful for later data integrity")
    parser.add_argument("--directory", required=True, help="The directory to validate")

    args = parser.parse_args()

    sys.exit(safe_validate(pathlib.Path(args.directory)))
