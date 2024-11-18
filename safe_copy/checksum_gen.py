import argparse
import pathlib
from safe_copy.managed_directory import ManagedDirectory
import sys


def checksum_gen(directory: pathlib.Path, force: bool) -> int:
    assert directory.is_dir()

    managed_source = ManagedDirectory(directory)
    if managed_source.has_checksums() and not force:
        print("checksums file found, see '--force' flag.")
        return 1

    print(f"Generating checksums for {directory}")
    managed_source.save_checksums()
    print("COMPLETE: Calculated checksums saved to disk")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Tool to calculate and save the checksum for a directory on disk")
    parser.add_argument("directory", help="The directory to generate the checksums for. If this already contains a "
                                          "sum.txt see '--force'", type=pathlib.Path)
    parser.add_argument('--force', help="If the directory already contains a sum.txt file force its contents to be "
                                        "replaced", action='store_true')

    args = parser.parse_args()

    sys.exit(checksum_gen(args.directory, args.force))
