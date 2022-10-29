from argparse import ArgumentParser
from argparse import Namespace
import os
from pathlib import Path
import shutil
from tempfile import mkdtemp

import pytest

from expnote.run import Run
from expnote.experiment import Experiment
from expnote.repository import Repository
from expnote.cli.commands import InitCmd
from expnote.cli.commands import NewCmd
from expnote.cli.commands import AddCmd
from expnote.cli.commands import StatusCmd
from expnote.cli.commands import ResetCmd
from expnote.cli.commands import RmCmd
from expnote.cli.commands import ShowCmd
from expnote.cli.commands import CommitCmd
from expnote.cli.commands import LogCmd
from expnote.cli.commands import EditCmd


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


@pytest.fixture
def sample_repo(work_dir) -> Path:
    repo = Repository.initialize()

    with repo.open_workspace() as workspace:
        run1 = Run('run1', params={}, metrics={})
        run2 = Run('run2', params={}, metrics={})
        exp = Experiment('title')
        repo.save_run(run1)
        repo.save_run(run2)
        exp = repo.save_experiment(exp)

        workspace.add_untracked_run(run1.id)
        workspace.add_untracked_run(run2.id)
        workspace.add_uncommitted_experiment(exp.id)

    yield repo


class TestInitCmd:

    def test_initialize(self, work_dir):
        parser = ArgumentParser()
        cmd = InitCmd(parser)
        cmd(parser.parse_args([]))
        Repository()  # do not raise an exception.

    def test_already_initialized(self, work_dir):
        Repository.initialize()
        parser = ArgumentParser()
        cmd = InitCmd(parser)
        cmd(parser.parse_args([]))  # do not raise an exception.


class TestNewCmd:

    def test(self, work_dir):
        repo = Repository.initialize()

        parser = ArgumentParser()
        cmd = NewCmd(parser)
        cmd(parser.parse_args(['title']))

        with repo.open_workspace() as ws:
            exp_ids = ws.uncommitted_experiments
            assert len(exp_ids) == 1

        exp = repo.get_experiment(exp_ids[0])
        exp.title == 'title'


class TestAddCmd:

    def test_single_run(self, sample_repo):
        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run1', '--to', '0']))
        with sample_repo.open_workspace() as workspace:
            assert workspace.assigned_runs['0'] == ['run1']

    def test_multi_runs(self, sample_repo):
        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run1', 'run2', '--to', '0']))
        with sample_repo.open_workspace() as workspace:
            assert workspace.assigned_runs['0'] == ['run1', 'run2']

    def test_not_existing_experiment(self, sample_repo):
        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run1', '--to', '99']))
        with sample_repo.open_workspace() as workspace:
            assert 'run1' in workspace.untracked_runs

    def test_auto_select(self, sample_repo):
        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run1']))
        with sample_repo.open_workspace() as workspace:
            assert workspace.assigned_runs['0'] == ['run1']

    def test_experiment_not_specified(self, sample_repo):
        # multiple choice -> auto selection is disabled
        with sample_repo.open_workspace() as workspace:
            workspace.add_uncommitted_experiment('1')
        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run1']))
        with sample_repo.open_workspace() as workspace:
            assert 'run1' in workspace.untracked_runs

    def test_not_existing_run(self, sample_repo):
        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run9']))
        with sample_repo.open_workspace() as workspace:
            assert workspace.assigned_runs['0'] == []

    def test_already_tracked_run(self, sample_repo):
        run9 = Run('run9', params={}, metrics={})
        sample_repo.save_run(run9)

        parser = ArgumentParser()
        cmd = AddCmd(parser)
        cmd(parser.parse_args(['run9']))
        with sample_repo.open_workspace() as workspace:
            assert workspace.assigned_runs['0'] == ['run9']


class TestStatusCmd:

    def test(self, sample_repo):
        parser = ArgumentParser()
        cmd = StatusCmd(parser)
        cmd(parser.parse_args([]))


class TestResetCmd:

    def test(self, sample_repo):
        with sample_repo.open_workspace() as workspace:
            workspace.assign_run_to_experiment('run1', '0')

        parser = ArgumentParser()
        cmd = ResetCmd(parser)
        cmd(parser.parse_args([]))

        with sample_repo.open_workspace() as workspace:
            assert workspace.assigned_runs['0'] == []


class TestRmCmd:

    def test(self, sample_repo):
        with sample_repo.open_workspace() as workspace:
            assert 'run1' in workspace.untracked_runs

        parser = ArgumentParser()
        cmd = RmCmd(parser)
        cmd(parser.parse_args(['run1']))

        with sample_repo.open_workspace() as workspace:
            assert not 'run1' in workspace.untracked_runs


class TestShowCmd:

    def test(self, sample_repo):
        parser = ArgumentParser()
        cmd = ShowCmd(parser)
        cmd(parser.parse_args(['run1']))


class TestCommit:

    def test(self, sample_repo):
        parser = ArgumentParser()
        cmd = CommitCmd(parser)
        cmd(parser.parse_args([]))

        with sample_repo.open_workspace() as workspace:
            assert not '0' in workspace.uncommitted_experiments


class TestLogCmd:

    def test(self, sample_repo):
        with sample_repo.open_workspace() as workspace:
            workspace.commit('0')

        parser = ArgumentParser()
        cmd = LogCmd(parser)
        cmd(parser.parse_args([]))


class TestEditCmd:

    def test(self, sample_repo):
        parser = ArgumentParser()
        cmd = EditCmd(parser)
        cmd(parser.parse_args(['--title', 'new title',
                               '--purpose', 'new purpose']))
        exp = sample_repo.get_experiment('0')
        assert exp.title == 'new title'
        assert exp.purpose == 'new purpose'
