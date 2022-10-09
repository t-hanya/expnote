"""
File based local repository.
"""


import json
from typing import List

from expnote.run import Run
from .file_storage import FileStorage


class LocalRepository:
    """File-based local repository."""

    def __init__(self) -> None:
        self._storage = FileStorage()

    @classmethod
    def initialize(cls) -> 'LocalRepository':
        FileStorage.initialize()
        return cls()

    def save_run(self, run: Run) -> None:
        """Save the run data."""
        data = {
            'id': run.id,
            'params': run.params,
            'metrics': run.metrics,
        }
        if run.step_metrics is not None:
            data['step_metrics'] = run.step_metrics
        obj_path = 'runs/' + run.id
        self._storage.save(json.dumps(data), obj_path)

    def get_run(self, run_id: str) -> Run:
        """Get the run data."""
        obj_path = 'runs/' + run_id
        data = json.loads(self._storage.get(obj_path))
        return Run(**data)

    def remove_run(self, run_id: str) -> None:
        """Remove the run data."""
        obj_path = 'runs/' + run_id
        self._storage.remove(obj_path)

    def find_runs(self, run_id_prefix: str) -> List[Run]:
        """Find runs with the specified run id pattern."""
        obj_paths = self._storage.glob('runs/{}*'.format(run_id_prefix))
        return [self.get_run(p[5:]) for p in obj_paths]

