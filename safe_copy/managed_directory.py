from __future__ import annotations
import hashlib
import os
import pathlib


class FileStats:
    """
    This is used to get the stats of a single file, specifically its md5 checksum. This is done in a lazy way
    to try and reduce the computation overhead

    :param filepath: This is the absolute path to the file to represent
    """
    def __init__(self, filepath: pathlib.Path):
        self.path = filepath
        self._checksum = None

    @property
    def checksum_method(self) -> str:
        return "md5"

    @property
    def checksum(self) -> str:
        if self._checksum is None:
            md5_hash = hashlib.md5()
            with open(self.path , "rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            self._checksum = md5_hash.hexdigest()
        return self._checksum


class ManagedDirectory:
    """
    This represents a managed directory and knows what its contents are, and the stats of those files

    param: managed_directory_root: This is the absolute root path of the directory to be managed
    """
    def __init__(self, managed_directory_root: pathlib.Path):
        self._root_dir = managed_directory_root
        self.directory_stats = self._get_directory_stats()
        self._checksum_file = pathlib.Path(managed_directory_root, 'sum.txt')

    def _get_directory_stats(self) -> list:
        managed_files = []
        for r, d, f in os.walk(self._root_dir):
            for file in f:
                abs_path = pathlib.Path(r, file)
                managed_files.append(FileStats(abs_path))
        return managed_files

    def relative_path(self, file: pathlib.Path):
        return file.path.relative_to(self._root_dir)

    def compare(self, other: ManagedDirectory) -> int:
        print(f"Comparing {other._root_dir} to {self._root_dir}")
        n_failures = 0
        for other_file in other.directory_stats:
            for file in self.directory_stats:
                if self.relative_path(file) == other.relative_path(other_file):
                    if file.checksum == other_file.checksum:
                        print(f"OK:     {file.path}")
                    else:
                        print(f"FAILED: {file.path}")
                        n_failures += 1
                    break
        return n_failures

    def save_checksums(self):
        with open(self._checksum_file, 'w') as checksums_file:
            for file in self.directory_stats:
                if self._checksum_file not in file.path.parts:
                    checksums_file.write(f"{file.checksum}\t{self.relative_path(file)}\n")

    def validate_checksums(self):
        n_failures = 0
        if not os.path.exists(self._checksum_file):
            print(f"Failed to find checksum file {self._checksum_file}")
            return n_failures

        print(f"Checking checksum from {self._checksum_file}")
        with open(self._checksum_file, 'r') as checksums_file:
            checksums = checksums_file.readlines()
            for checksum in checksums:
                md5_checksum = checksum.split('\t')[0].strip()
                rel_path = checksum.split('\t')[1].strip()
                path = pathlib.Path(self._root_dir, rel_path)

                for file in self.directory_stats:
                    if file.path == path:
                        if file.checksum == md5_checksum:
                            print(f"OK:     {file.path}")
                        else:
                            print(f"FAILED: {file.path}")
                            n_failures += 1
                        break
        return n_failures
