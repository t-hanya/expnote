"""
A memory object to gather and organize run data.
"""


from typing import Optional
from typing import Tuple

from expnote.run import Run
from expnote.repository import Repository


_memories = []


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Recursively merge two nested dictionaries."""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for key in dict2:
        if key in dict1:
            dict1[key] = merge_dicts(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


class Memory:
    """A memory to gather and organize run data."""

    def __init__(self,
                 run_id: str,
                 repo: Optional[Repository] = None
                ) -> None:
        self.run_id = run_id
        self.repo = repo
        self.params = {}
        self.metrics = {}
        self.step_metrics = None

    def __enter__(self) -> 'Memory':
        global _memories
        _memories.append(self)
        return self

    def __exit__(self, *args) -> None:
        global _memories
        _memories.pop()

    def set_params(self,
                   data: dict
                  ) -> None:
        """Set the params data."""
        self.params = merge_dicts(self.params, data)

    def set_metrics(self,
                    data: dict,
                    step: Optional[Tuple[int, str]] = None
                   ) -> None:
        """Set the metrics data."""

        if step is None:
            for k, v in data.items():
                self.metrics[k] = v
            return

        if self.step_metrics is None:
            self.step_metrics = []

        step_num, step_key = step
        for step_data in self.step_metrics:
            if step_data.get(step_key, None) == step_num:
                for k, v in data.items():
                    step_data[k] = v
                    return

        step_data = {step_key: step_num}
        for k, v in data.items():
            step_data[k] = v
        self.step_metrics.append(step_data)

    def flush(self) -> None:
        """Flush run data."""
        if self.repo is not None:
            run = Run(
                id=self.run_id,
                params=self.params,
                metrics=self.metrics,
                step_metrics=self.step_metrics
            )
            self.repo.save_run(run)


def get_current_memory() -> Memory:
    global _memories
    return _memories[-1]


def set_params(data: dict) -> None:
    """Write params to the current memory."""
    mem = get_current_memory()
    mem.set_params(data)


def set_metrics(data: dict,
                step: Optional[Tuple[int, str]] = None
               ) -> None:
    """Write metrics to the current memory."""
    mem = get_current_memory()
    mem.set_metrics(data, step=step)
