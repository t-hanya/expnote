import os
from pathlib import Path
import shutil
from tempfile import mkdtemp

import pytest

from expnote.repository import Repository
from expnote.recording import Recorder


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


class TestRecorder:
    def test(self, work_dir):

        repo = Repository.initialize()

        recorder = Recorder(
            repo=repo
        )

        @recorder.scope
        def main():
            recorder.params({'lr': 0.1})
            recorder.metrics({'acc': 0.9})
            for i in range(5):
                recorder.metrics({'loss': 5 - i}, step=(i, 'epoch'))
            recorder.info({'tag': 'train'})

        main()

        runs = repo.find_runs('')
        assert len(runs) == 1

        run = runs[0]
        assert run.params == {'lr': 0.1}
        assert run.metrics == {'acc': 0.9}
        assert run.step_metrics == [
            {'epoch': 0, 'loss': 5},
            {'epoch': 1, 'loss': 4},
            {'epoch': 2, 'loss': 3},
            {'epoch': 3, 'loss': 2},
            {'epoch': 4, 'loss': 1}
        ]
        assert 'start_time' in run.info
        assert 'end_time' in run.info
        assert run.info['status'] == 'complete'
        assert run.info['tag'] == 'train'
