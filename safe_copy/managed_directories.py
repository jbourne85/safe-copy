import hashlib
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
    def checksum_method(self):
        return "md5"

    @property
    def checksum(self):
        if self._checksum is None:
            md5_hash = hashlib.md5()
            with open(self.path , "rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            self._checksum = md5_hash.hexdigest()
        return self._checksum