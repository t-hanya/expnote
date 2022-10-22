import os
from pathlib import Path
import shutil
from tempfile import mkdtemp

import pytest
from PIL import Image

from expnote.run import Run
from expnote.note import Table
from expnote.note import Figure
from expnote.note import Note
from expnote.experiment import Experiment
from expnote.repository.local_repo import LocalRepository
from expnote.repository.local_repo import FileNameAssigner


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

    def test_save_get_experiment(self, work_dir):
        repo = LocalRepository.initialize()

        exp = Experiment(title='title')
        exp.purpose = 'purpose'
        exp.conclusion = 'conclusion'
        exp.run_ids = ['run1', 'run2', 'run3']
        exp.add(Table(['a', 'b', 'c'],
                      [[1, 2, 3], [4, 5, 6]]))
        exp.add(Figure(Image.new('RGB', (20, 10))))
        exp.add(Note('note'))

        exp = repo.save_experiment(exp)
        assert exp.id is not None

        exp = repo.get_experiment(exp.id)
        assert exp.title == 'title'
        assert exp.purpose == 'purpose'
        assert exp.conclusion == 'conclusion'
        assert exp.run_ids == ['run1', 'run2', 'run3']
        assert exp.notes[0].columns == ['a', 'b', 'c']
        assert exp.notes[0].rows == [[1, 2, 3], [4, 5, 6]]
        assert exp.notes[1].image.size == (20, 10)
        assert exp.notes[2].note == 'note'

    def test_remove_experiment(self, work_dir):
        repo = LocalRepository.initialize()
        exp = Experiment(title='title')
        exp = repo.save_experiment(exp)
        repo.remove_experiment(exp.id)
        with pytest.raises(KeyError):
            repo.get_experiment(exp.id)

    def test_find_experiments(self, work_dir):
        repo = LocalRepository.initialize()
        repo.save_experiment(Experiment(title='title1'))
        repo.save_experiment(Experiment(title='title2'))
        repo.save_experiment(Experiment(title='title3'))

        e4 = repo.save_experiment(Experiment(title='title4'))
        repo.remove_experiment(e4.id)  # removed experiment should be ignored

        exps = repo.find_experiments()
        assert len(exps) == 3
        assert [e.title for e in exps] == ['title1', 'title2', 'title3']

        exps = repo.find_experiments(limit=2)
        assert len(exps) == 2
        assert [e.title for e in exps] == ['title1', 'title2']

        exps = repo.find_experiments(limit=2, reverse=True)
        assert len(exps) == 2
        assert [e.title for e in exps] == ['title3', 'title2']


class TestFileNameAssigner:

    def test(self):
        titles = ('Loss curve', None, 'Loss curve', None)
        assigner = FileNameAssigner()
        ret = [assigner(title) for title in titles]
        assert ret == ['loss-curve1.png', 'figure1.png',
                       'loss-curve2.png', 'figure2.png']
