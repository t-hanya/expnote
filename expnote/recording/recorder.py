"""
A helper class to record run data.
"""


from functools import wraps
from typing import Optional
from typing import Tuple
import uuid

from expnote.run import Run
from expnote.repository import Repository
from expnote.recording.memory import Memory
from expnote.recording.memory import set_params
from expnote.recording.memory import set_metrics


class Recorder:
    """A helper class to record run data."""

    def __init__(self,
                 repo: Optional[Repository] = None,
                ) -> None:
        if repo is None:
            repo = Repository()
        self.repo = repo

    def scope(self, func: callable) -> callable:
        """Function decorator to add recording functionality."""

        @wraps(func)
        def wrapped_func(*args, **kwargs):

            memory = Memory(
                run_id=uuid.uuid4().hex,
                repo=self.repo,
            )
            with memory:
                # execute the function
                ret = func(*args, **kwargs)

            memory.flush()

            return ret

        return wrapped_func

    def params(self, data: dict) -> None:
        set_params(data)

    def metrics(self,
                data: dict,
                step: Optional[Tuple[int, str]] = None
               ) -> None:
        set_metrics(data, step=step)
