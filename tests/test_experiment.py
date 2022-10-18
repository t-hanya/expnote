import pytest

from expnote.experiment import Experiment
from expnote.experiment import Workspace
from expnote.note import Note


class TestExperiment:

    def test(self):
        exp = Experiment(title='title')
        exp.add(Note('content'))

        assert 'title' in str(exp)
        assert 'content' in str(exp)


class TestWorkspace:

    def test_add_untracked_run(self):
        workspace = Workspace()
        workspace.add_untracked_run('run1')
        assert workspace.untracked_runs == ['run1']
        workspace.add_untracked_run('run2')
        assert workspace.untracked_runs == ['run1', 'run2']

    def test_add_uncommitted_experiment(self):
        workspace = Workspace()
        workspace.add_uncommitted_experiment('exp1')
        assert workspace.uncommitted_experiments == ['exp1']
        workspace.add_uncommitted_experiment('exp2')
        assert workspace.uncommitted_experiments == ['exp1', 'exp2']

    def test_assign_run_to_experiment(self):
        workspace = Workspace(
            untracked_runs=['run1', 'run2'],
            uncommitted_experiments=['exp1', 'exp2'],
        )
        workspace.assign_run_to_experiment('run1', 'exp1')
        assert workspace.assigned_runs == {'exp1': ['run1'], 'exp2': []}
        assert workspace.untracked_runs == ['run2']

    def test_assign_run_to_experiment_key_error(self):
        workspace = Workspace()
        with pytest.raises(KeyError):
            workspace.assign_run_to_experiment('run1', 'exp1')

    def test_assign_run_to_experiment_not_in_list(self):
        workspace = Workspace(
            uncommitted_experiments=['exp1', 'exp2']
        )
        workspace.assign_run_to_experiment('run9', 'exp1')
        assert workspace.assigned_runs == {'exp1': ['run9'], 'exp2': []}

    def test_reset_assignments(self):
        workspace = Workspace(
            untracked_runs=['run1', 'run2'],
            uncommitted_experiments=['exp1', 'exp2'],
            assigned_runs={'exp1': ['run1', 'run9'], 'exp2': []}
        )
        assert workspace.assigned_runs == {'exp1': ['run1', 'run9'], 'exp2': []}
        assert workspace.untracked_runs == ['run2']  # run1 is excluded.

        workspace.reset_assignments()
        assert workspace.assigned_runs == {'exp1': [], 'exp2': []}
        assert workspace.untracked_runs == ['run1', 'run2']

    def test_remove_run(self):
        workspace = Workspace(
            untracked_runs=['run1', 'run2'],
            uncommitted_experiments=['exp1', 'exp2'],
            assigned_runs={'exp1': ['run1']},
        )
        # remove from untracked runs
        workspace.remove_run('run2')
        assert workspace.assigned_runs == {'exp1': ['run1'], 'exp2': []}
        assert workspace.untracked_runs == []

        # remove from both untracked runs and assigned runs
        workspace.remove_run('run1')
        assert workspace.assigned_runs == {'exp1': [], 'exp2': []}
        assert workspace.untracked_runs == []

    def test_remove_run_key_error(self):
        workspace = Workspace()
        with pytest.raises(KeyError):
            workspace.remove_run('run9')

    def test_commit(self):
        workspace = Workspace(
            untracked_runs=['run1', 'run2'],
            uncommitted_experiments=['exp1', 'exp2'],
            assigned_runs={'exp1': ['run1', 'run9'], 'exp2': []}
        )
        workspace.commit('exp1')
        assert workspace.untracked_runs == ['run2']
        assert workspace.uncommitted_experiments == ['exp2']
        assert workspace.assigned_runs == {'exp2': []}

        workspace.commit()  # exp2 is committed (no other candidate)
        assert workspace.uncommitted_experiments == []
        assert workspace.assigned_runs == {}

    def test_commit_key_error(self):
        workspace = Workspace(
            uncommitted_experiments=['exp1']
        )
        with pytest.raises(KeyError):
            workspace.commit('exp9')

    def test_commit_no_candidate(self):
        workspace = Workspace()
        with pytest.raises(IndexError):
            workspace.commit('exp9')
