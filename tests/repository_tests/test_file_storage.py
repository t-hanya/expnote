import os
from pathlib import Path
import shutil
from tempfile import mkdtemp

import pytest

from expnote.repository.file_storage import FileStorage
from expnote.repository.file_storage import DIR_NAME


@pytest.fixture
def work_dir() -> Path:
    org_dir = os.getcwd()
    try:
        tmp_dir = mkdtemp()
        tmp_dir_path = Path(tmp_dir).resolve()
        os.chdir(tmp_dir_path)
        yield tmp_dir_path

    finally:
        os.chdir(org_dir)
        shutil.rmtree(tmp_dir)


class TestFileStorage:

    def test_not_initialized(self, work_dir):
        with pytest.raises(FileNotFoundError):
            FileStorage()

    def test_initialize(self, work_dir):
        storage = FileStorage.initialize()
        root = work_dir / DIR_NAME
        assert storage.root == root
        assert root.is_dir()

    def test_find_storage_dir(self, work_dir):
        FileStorage.initialize()
        root = work_dir / DIR_NAME

        storage = FileStorage()
        assert storage.root == root

        sub_dir = work_dir / 'subdir'
        sub_dir.mkdir()
        os.chdir(sub_dir)

        storage = FileStorage()
        assert storage.root == root

    @pytest.mark.parametrize('obj_path', ['test', 'tests/abcdefg'])
    def test_get_key_error(self, work_dir, obj_path):
        storage = FileStorage.initialize()
        with pytest.raises(KeyError):
            storage.get(obj_path)

    @pytest.mark.parametrize('obj_path', ['test', 'tests/abcdefg'])
    def test_remove_key_error(self, work_dir, obj_path):
        storage = FileStorage.initialize()
        with pytest.raises(KeyError):
            storage.remove(obj_path)

    @pytest.mark.parametrize('obj_path_pattern', ['t*', 'tests/*'])
    def test_glob_no_result(self, work_dir, obj_path_pattern):
        storage = FileStorage.initialize()
        obj_paths = storage.glob(obj_path_pattern)
        assert len(obj_paths) == 0

    @pytest.mark.parametrize('obj_path', ['test', 'tests/abcdefg'])
    def test_save_get(self, work_dir, obj_path):
        storage = FileStorage.initialize()
        storage.save('content', obj_path)

        storage = FileStorage()
        ret = storage.get(obj_path)
        assert ret == 'content'

    @pytest.mark.parametrize('obj_path', ['test', 'tests/abcdefg'])
    def test_save_remove(self, work_dir, obj_path):
        storage = FileStorage.initialize()
        storage.save('content', obj_path)

        storage = FileStorage()
        storage.remove(obj_path)
        with pytest.raises(KeyError):
            storage.get(obj_path)

    @pytest.mark.parametrize('prefix', ['', 'tests/'])
    def test_save_glob(self, work_dir, prefix):
        storage = FileStorage.initialize()
        storage.save('', prefix + 'aaa1')
        storage.save('', prefix + 'aaa2')
        storage.save('', prefix + 'aaa3')
        storage.save('', prefix + 'bbb1')
        storage.save('', 'ccc1')

        storage = FileStorage()
        obj_paths = storage.glob(prefix + 'aaa*')

        assert set(obj_paths) == {prefix + 'aaa1',
                                  prefix + 'aaa2',
                                  prefix + 'aaa3'}
