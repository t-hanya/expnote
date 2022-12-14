"""
A run data structure.
"""


from dataclasses import dataclass
from typing import Optional
from typing import List
from typing import Tuple
from typing import TypedDict
from typing import Literal


class RunInfo(TypedDict):
    """A run info data structure."""
    start_time: str
    end_time: Optional[str] = None
    status: Literal['running', 'complete', 'failed', 'interrupted']


@dataclass
class Run:
    """A run data structure."""
    id: str
    params: dict
    metrics: dict
    step_metrics: Optional[list] = None
    info: Optional[RunInfo] = None


@dataclass
class RunGroup:
    """A run group data structure."""

    runs: List[Run]
    id: Tuple[str, ...]
    params: dict
    metrics: dict
    step_metrics: Optional[list] = None
