"""
Define an experiment object to organize facts and thoughts.
"""


from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from expnote.note import Note
from expnote.note import Figure
from expnote.note import Table


Content = Union[Note, Figure, Table]


class Experiment:
    """An experiment object to organize facts and thoughts."""

    def __init__(self,
                 title: str,
                 purpose: Optional[str] = None,
                 conclusion: Optional[str] = None,
                 notes: Optional[List[Content]] = None,
                 id: Optional[str] = None,
                 run_ids: Optional[List[str]] = None,
                ) -> None:
        self.title = title
        self.purpose = purpose
        self.conclusion = conclusion
        self.notes = notes

        self.id = id
        self.run_ids = run_ids

    def add(self, content: Content) -> None:
        if self.notes is None:
            self.notes = []
        self.notes.append(content)

    def __str__(self) -> str:
        content = f'# {self.title}'
        if self.purpose is not None:
            content += f'\n\nPurpose: {self.purpose}'
        if self.purpose is not None:
            content += f'\n\nConclusion: {self.conclusion}'
        if self.notes is not None:
            note_contents = [str(note) for note in self.notes]
            content += '\n\n' + '\n\n'.join(note_contents)
        return content


class Workspace:
    """A workspace object to organize runs and experiments."""

    def __init__(self,
                 untracked_runs: Optional[List[str]] = None,
                 uncommitted_experiments: Optional[List[str]] = None,
                 assigned_runs: Optional[Dict[str, List[str]]] = None
                ) -> None:
        self._untracked_runs = untracked_runs
        self._uncommitted_experiments = uncommitted_experiments
        self._assigned_runs = assigned_runs

    @property
    def untracked_runs(self) -> List[str]:
        """Untracked run id list.

        Assigned runs are excluded.
        """
        assigned_runs = set()
        for exp_id, run_ids in self.assigned_runs.items():
            for run_id in run_ids:
                assigned_runs.add(run_id)
        return [run_id for run_id in (self._untracked_runs or [])
                if not run_id in assigned_runs]

    @property
    def uncommitted_experiments(self) -> List[str]:
        """Uncommited experiment id list."""
        if self._uncommitted_experiments is None:
            return []
        else:
            return self._uncommitted_experiments.copy()

    @property
    def assigned_runs(self) -> Dict[str, List[str]]:
        """Assigned run id list for each experiment."""
        assigned_runs = self._assigned_runs or {}
        return {k: assigned_runs.get(k, [])
                for k in self.uncommitted_experiments}

    def add_untracked_run(self, run_id: str) -> None:
        """Add the run id to the untracked runs."""
        if self._untracked_runs is None:
            self._untracked_runs = []
        if not run_id in self.untracked_runs:
            self._untracked_runs.append(run_id)

    def add_uncommitted_experiment(self, experiment_id: str) -> None:
        """Add the experiment id to the uncommitted experiments."""
        if self._uncommitted_experiments is None:
            self._uncommitted_experiments = []
        if not experiment_id in self._uncommitted_experiments:
            self._uncommitted_experiments.append(experiment_id)

    def assign_run_to_experiment(self,
                                 run_id: str,
                                 experiment_id: str
                                ) -> None:
        """Assign the run id to the specified experiment."""
        if not experiment_id in self.uncommitted_experiments:
            raise KeyError(
                f'No uncommitted experiment with the id: {experiment_id}')
        if self._assigned_runs is None:
            self._assigned_runs = {}
        if not experiment_id in self._assigned_runs:
            self._assigned_runs[experiment_id] = []
        if not run_id in self._assigned_runs[experiment_id]:
            self._assigned_runs[experiment_id].append(run_id)

    def reset_assignments(self) -> None:
        """Reset all run-to-experiment assignments."""
        self._assigned_runs = None

    def remove_run(self, run_id: str) -> None:
        """Remove run from untracked runs and assined runs."""
        found = False

        if run_id in (self._untracked_runs or []):
            self._untracked_runs.remove(run_id)
            found = True

        for exp_id, assigned_run_ids in self.assigned_runs.items():
            if run_id in assigned_run_ids:
                self._assigned_runs[exp_id].remove(run_id)
                found = True

        if not found:
            msg = ('Run id is not found in both untracked runs and '
                   'assigned runs ({}).').format(run_id)
            raise KeyError(msg)

    def commit(self,
               experiment_id: Optional[str] = None
              ) -> None:
        """Remove from uncommited experiments and update untracked runs."""
        if not self.uncommitted_experiments:
            raise IndexError('Uncommitted experiment does not exist.')

        if experiment_id is None:
            if len(self.uncommitted_experiments) == 1:
                experiment_id = self.uncommitted_experiments[0]
            else:
                msg = ('Specify experiment id to be committed. '
                       'There are multiple candidates: {}').format(
                    ', '.join(self.uncommitted_experiments))
                raise ValueError(msg)

        if not experiment_id in self.uncommitted_experiments:
            raise KeyError(
                f'No uncommitted experiment with the id: {experiment_id}')

        assigned_runs = self.assigned_runs[experiment_id]
        if (self._assigned_runs is not None and
            experiment_id in self._assigned_runs):
            del self._assigned_runs[experiment_id]

        self._uncommitted_experiments.remove(experiment_id)
        for run_id in assigned_runs:
            if run_id in self._untracked_runs:
                self._untracked_runs.remove(run_id)
