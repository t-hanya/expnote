"""
A run data structure.
"""


from dataclasses import dataclass
from typing import Optional
from typing import List
from typing import Tuple


@dataclass
class Run:
    """A run data structure."""
    id: str
    params: dict
    metrics: dict
    step_metrics: Optional[list] = None


@dataclass
class RunGroup:
    """A run group data structure."""

    runs: List[Run]
    id: Tuple[str, ...]
    params: dict
    metrics: dict
    step_metrics: Optional[list] = None
