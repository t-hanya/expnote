"""
A run data structure.
"""


from dataclasses import dataclass
from typing import Optional


@dataclass
class Run:
    """A run data structure."""
    id: str
    params: dict
    metrics: dict
    step_metrics: Optional[list] = None
