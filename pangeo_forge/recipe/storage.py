from dataclasses import dataclass
from contextlib import closing, contextmanager
import fsspec


@dataclass
class Target:
    """Representation of a storage target for Pangeo Forge.
    Attributes
    ----------
    fs : FileSystemSpec.AbtractFileSystem
        The filesystem we are writing to. Should be instantiated outside this
        class.
    path : str
        The path where the target data will be saved.
    """

    fs: fsspec.AbstractFileSystem
    path: str

    def get_mapper(self):
        # don't want to use this because we want to use a fancier Zarr FSStore
        return self.fs.get_mapper(self.path)


def _hash_path(path: str) -> str:
    return str(hash(path))


@dataclass
class InputCache:
    """Representation of an intermediate storage location where remote files
    Can be cached locally.

    Attributes
    ----------
    fs : FileSystemSpec.AbtractFileSystem
        The filesystem we are writing to. Should be instantiated outside this
        class.
    prefix : str
        A path prepended to all paths.
    """

    fs: fsspec.AbstractFileSystem
    prefix: str = ""

    def _full_path(self, path):
        return os.path.join(self.prefix, _hash_path(path))

    def exists(self, path):
        return self.fs.exists(self._full_path(path))

    def rm(self, path):
        self.fs.rm(self._full_path(path))

    @contextmanager
    def open(self, path):
        with self.fs.open(self._full_path(path)) as f:
            yield f