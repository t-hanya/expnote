"""
File based local repository.
"""


import json
from typing import List
from typing import Optional
from typing import Tuple

from expnote.run import Run
from expnote.note import Table
from expnote.note import Figure
from expnote.note import Note
from expnote.experiment import Experiment
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

    def _generate_experiment_id(self) -> str:
        prefix = 'experiments/'
        ids = [obj_path[len(prefix):] for obj_path
               in self._storage.glob(prefix + '*')]
        decimal_ids = [int(id_) for id_ in ids if id_.isdecimal()]
        if decimal_ids:
            max_id = max(decimal_ids)
        else:
            max_id = -1
        return str(max_id + 1)

    def save_experiment(self, experiment: Experiment) -> Experiment:
        """Save the experiment data."""
        # assign experiment id
        if experiment.id is None:
            experiment.id = self._generate_experiment_id()

        # convert experiment data
        data = {
            'title': experiment.title,
            'purpose': experiment.purpose,
            'conclusion': experiment.conclusion,
            'run_ids': experiment.run_ids,
            'notes': [],
        }
        files = []
        fig_name_assigner = FileNameAssigner(
            default_stem='figure',
            ext='.png'
        )
        for note in (experiment.notes or []):
            if type(note) == Note:
                data['notes'].append({
                    'type': 'note',
                    'note': note.note,
                    'title': note.title
                })
            elif type(note) == Table:
                data['notes'].append({
                    'type': 'table',
                    'columns': note.columns,
                    'rows': note.rows,
                    'note': note.note,
                    'title': note.title
                })
            elif type(note) == Figure:
                file_name = fig_name_assigner(note.title)
                file_path = 'figures/' + file_name
                data['notes'].append({
                    'type': 'figure',
                    'note': note.note,
                    'title': note.title,
                    '_file_path': file_path,
                })
                files.append({
                    'data': note.image,
                    'path': file_path,
                    'type': 'image'
                })

        # save data
        obj_root = 'experiments/' + experiment.id
        self._storage.save(
            json.dumps(data, indent=2),
            obj_root + '/data',
        )
        for file in files:
            obj_path = obj_root + '/' + file['path']
            self._storage.save(
                file['data'],
                obj_path,
                data_type=file['type']
            )
        return experiment

    def get_experiment(self, experiment_id: str) -> Experiment:
        """Get the experiment data."""
        obj_root = 'experiments/' + experiment_id
        data = json.loads(self._storage.get(obj_root + '/data'))
        notes = []
        for note_data in data['notes']:
            if note_data['type'] == 'note':
                notes.append(Note(
                    title=note_data['title'],
                    note=note_data['note']
                ))
            elif note_data['type'] == 'table':
                notes.append(Table(
                    columns=note_data['columns'],
                    rows=note_data['rows'],
                    title=note_data['title'],
                    note=note_data['note'],
                ))
            elif note_data['type'] == 'figure':
                obj_path = obj_root + '/' + note_data['_file_path']
                notes.append(Figure(
                    image=self._storage.get(obj_path, data_type='image'),
                    title=note_data['title'],
                    note=note_data['note'],
                ))
        experiment = Experiment(
            id=experiment_id,
            title=data['title'],
            purpose=data['purpose'],
            conclusion=data['conclusion'],
            notes=notes,
            run_ids=data['run_ids']
        )
        return experiment

    def remove_experiment(self, experiment_id: str) -> None:
        """Remove the experiment data."""
        obj_root = 'experiments/' + experiment_id
        fig_paths = self._storage.glob(obj_root + '/figures/*')
        for fig_path in fig_paths:
            self._storage.remove(fig_path)
        self._storage.remove(obj_root + '/data')

    def find_experiments(self,
                         limit: Optional[int] = None,
                         reverse: bool = False
                        ) -> List[Experiment]:
        """Find experiments."""
        exp_ids = [path[12:] for path in self._storage.glob('experiments/*')]

        to_int = lambda id_: (int(id_) if id_.isdecimal() else id_)
        exp_ids = sorted(exp_ids, key=lambda id_: to_int(id_))
        if reverse:
            exp_ids = list(reversed(exp_ids))
        if limit is not None:
            exp_ids = exp_ids[:limit]
        experiments = [self.get_experiment(exp_id) for exp_id in exp_ids]
        return experiments


class FileNameAssigner:
    """Assign file names using note titles."""

    def __init__(self,
                 default_stem: str = 'figure',
                 ext: str = '.png'
                ) -> None:
        self.used_names = set()
        self.default_stem = default_stem
        self.ext = ext

    def __call__(self, title: Optional[str] = None) -> str:
        if title:
            stem = title.lower().replace(' ', '-')
        else:
            stem = self.default_stem

        number = 1
        while True:
            name = stem + str(number) + self.ext
            if not name in self.used_names:
                self.used_names.add(name)
                return name
            number += 1
