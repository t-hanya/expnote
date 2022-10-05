import os
from pathlib import Path
import shutil
from tempfile import mkdtemp

import pytest

from expnote.run import Run
from expnote.repository.local_repo import LocalRepository


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


sample_run_data = {
    'id': '1',
    'params': {'lr': 0.1, 'wd': 1e-4},
    'metrics': {'acc': 0.9},
    'step_metrics': [{'epoch': 0, 'loss': 1.5}],
}


class TestLocalRepository:

    def test_not_initialized(self, work_dir):
        with pytest.raises(FileNotFoundError):
            repo = LocalRepository()

    def test_initialize(self, work_dir):
        LocalRepository.initialize()
        repo = LocalRepository()

    def test_save_get_run(self, work_dir):
        repo = LocalRepository.initialize()
        run = Run(**sample_run_data)
        repo.save_run(run)
        run2 = repo.get_run(run.id)
        assert run2 == run

    def test_remove_run(self, work_dir):
        repo = LocalRepository.initialize()
        run = Run(**sample_run_data)
        repo.save_run(run)
        repo.remove_run(run.id)
        with pytest.raises(KeyError):
            repo.get_run(run.id)

    def test_find_runs(self, work_dir):
        repo = LocalRepository.initialize()
        repo.save_run(Run(id='a111', params={}, metrics={}))
        repo.save_run(Run(id='a222', params={}, metrics={}))
        repo.save_run(Run(id='b333', params={}, metrics={}))

        ret = repo.find_runs('c')
        assert len(ret) == 0

        ret = repo.find_runs('a1')
        assert len(ret) == 1
        assert ret[0].id == 'a111'

        ret = repo.find_runs('a')
        assert len(ret) == 2
        assert set(r.id for r in ret) == set(('a111', 'a222'))
