"""
Local file storage.
"""


from contextlib import contextmanager
from typing import Optional
from typing import List
from typing import Union
from pathlib import Path

import filelock
from PIL import Image


DIR_NAME = '.expnote'


def _find_storage_dir(base_dir: Union[str, Path]) -> Optional[Path]:
    """Find storage directory."""
    if base_dir is None:
        base_dir = '.'
    if type(base_dir) == str:
        base_dir = Path(base_dir)

    check_dir = base_dir.resolve()
    while True:
        if (check_dir / DIR_NAME).is_dir():
            return check_dir / DIR_NAME
        if check_dir.parent == check_dir:
            # reach the file system root -> not found
            return None
        check_dir = check_dir.parent


class FileStorage:
    """Local file based object storage."""

    def __init__(self,
                 base_dir: Optional[Union[str, Path]] = None
                ) -> None:
        self.root = _find_storage_dir(base_dir)
        if self.root is None:
            raise FileNotFoundError(
                'Local storage not found (dir name: {})'.format(DIR_NAME))

    @classmethod
    def initialize(cls) -> 'FileStorage':
        Path(DIR_NAME).mkdir()
        return cls()

    def _obj_path_to_file_path(self, obj_path: str) -> Path:
        """Get file path from object path str."""
        elems = obj_path.split('/')
        if any([len(s) == 0 for s in obj_path.split('/')]):
            msg = 'Empty path element is not allowed (obj_path: {})'.format(
                obj_path)
            raise ValueError(msg)
        return self.root / obj_path

    def save(self, data: str, obj_path: str, data_type: str = 'text') -> None:
        """Save an object to the storage.

        Args:
            data (str or PIL.Image.Image): An object data.
            obj_path (str): An object path for the data.
            data_type (str, optional) : Data type in ('text', 'image').
        """
        file_path = self._obj_path_to_file_path(obj_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if data_type == 'text':
            with file_path.open('w') as f:
                f.write(data)
        elif data_type == 'image':
            data.save(file_path)
        else:
            raise ValueError('Unknown data type ({})'.format(data_type))

    def get(self, obj_path: str, data_type: str = 'text') -> str:
        """Get an object from the storage.

        Args:
            obj_path (str): An object path.
            data_type (str, optional) : Data type in ('text', 'image').

        Raises:
            KeyError for non-existent object path.

        Returns:
            str or PIL.Image.Image: The object data content.
        """
        file_path = self._obj_path_to_file_path(obj_path)
        if not file_path.is_file():
            raise KeyError('Object not found ({})'.format(obj_path))
        if data_type == 'text':
            with file_path.open() as f:
                data = f.read()
        elif data_type == 'image':
            data = Image.open(file_path)
        else:
            raise ValueError('Unknown data type ({})'.format(data_type))
        return data

    def remove(self, obj_path: str) -> None:
        """Remove an object from the storage.

        Args:
            obj_path (str): An object path.

        Raises:
            KeyError for non-existent object path.
        """
        file_path = self._obj_path_to_file_path(obj_path)
        try:
            file_path.unlink()
        except FileNotFoundError:
            raise KeyError('Object not found ({})'.format(obj_path))

        rel_path = file_path.relative_to(self.root)
        if len(rel_path.parts) > 1:
            parent_dir = file_path.parent
            if len(list(parent_dir.iterdir())) == 0:
                parent_dir.rmdir()

    def glob(self, obj_path_pattern: str) -> List[str]:
        """Find object paths matching with the pattern.

        Args:
            obj_path_pattern (str): Object path pattern (e.g. runs/abc*)

        Returns:
            list of str: Object path list that match the specified pattern.
        """
        file_path_pattern = self._obj_path_to_file_path(obj_path_pattern)

        parent_dir = file_path_pattern.parent
        file_name_pattern = file_path_pattern.parts[-1]
        found = parent_dir.glob(file_name_pattern)

        obj_paths = [str(p.relative_to(self.root)) for p in found]
        return obj_paths

    @contextmanager
    def lock(self, obj_path: str) -> filelock.AcquireReturnProxy:
        """Aqruire file lock."""
        file_path = self._obj_path_to_file_path(obj_path)
        parent_dir = file_path.parent
        file_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = parent_dir / (file_path.name + '.lock')
        with filelock.FileLock(str(lock_path)) as proxy:
            yield proxy
