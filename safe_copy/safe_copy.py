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
        managed_destination.save_checksums()
    else:
        print(f"WARNING: {result} computed checksums did not match")
    return result


def main():
    parser = argparse.ArgumentParser(description="Tool to safely copy fioles from one folder to anouther, validating "
                                                 "the operation and saving checksums for later validation")
    parser.add_argument("--source", required=True, help="The source directory to copy from")
    parser.add_argument("--destination", required=True, help="The destination to copy into")

    args = parser.parse_args()

    sys.exit(safe_copy(pathlib.Path(args.source), pathlib.Path(args.destination)))
