import argparse
import os
import sys
from safe_copy.managed_directory import ManagedDirectory
import pathlib
import shutil


def safe_copy(source, destination):
    assert source.is_dir()
    assert destination.is_dir()

    destination = pathlib.Path(os.path.join(destination, source.parts[-1]))
    print(f"Copying {source} -> {destination}")

    managed_source = ManagedDirectory(source.absolute())
    managed_destination = ManagedDirectory(destination.absolute())

    shutil.copytree(source, destination, dirs_exist_ok=True)

    result = managed_destination.compare(managed_source)
    if result == 0:
        print("SUCCESS: All files computed checksums matched")
    else:
        print(f"WARNING: {result} computed checksums did not match")
    return result


def main():
    parser = argparse.ArgumentParser(description="Tool to train the parameters of the cryptodec")
    parser.add_argument("--source", required=True, help="The source directory to copy from")
    parser.add_argument("--destination", required=True, help="The destination to copy into")

    args = parser.parse_args()

    sys.exit(safe_copy(pathlib.Path(args.source), pathlib.Path(args.destination)))
