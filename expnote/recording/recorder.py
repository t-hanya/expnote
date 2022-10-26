"""
A helper class to record run data.
"""


from contextlib import ExitStack
from functools import wraps
from typing import Optional
from typing import Tuple
import uuid

from expnote.run import Run
from expnote.repository import Repository
from expnote.recording.memory import Memory
from expnote.recording.memory import set_params
from expnote.recording.memory import set_metrics
from expnote.recording.memory import set_info
from expnote.recording.collectors import RunInfoCollector


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

            run_id = uuid.uuid4().hex
            memory = Memory(
                run_id=run_id,
                repo=self.repo,
            )
            with memory:
                with ExitStack() as stack:
                    stack.enter_context(RunInfoCollector())
                    memory.flush()
                    with self.repo.open_workspace() as ws:
                        ws.add_untracked_run(run_id)

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

    def info(self, data: dict) -> None:
        set_info(data)
