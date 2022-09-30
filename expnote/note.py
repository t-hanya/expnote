"""
Data structures to represent the contents of an experiment notebook.
"""


from dataclasses import dataclass
from typing import List
from typing import Any

from PIL import Image


@dataclass
class Table:
    """A table data structure."""
    columns: List[str]
    rows: List[List[Any]]

    def __str__(self) -> str:
        width_arr = []
        for i in range(len(self.columns)):
            contents = [r[i] for r in self.rows] + [self.columns[i]]
            max_len = max([len(str(v)) for v in contents])
            width_arr.append(max_len)
        lines = []
        lines.append(' ' + ' | '.join([col.ljust(w) for col, w
                                       in zip(self.columns, width_arr)]))
        lines.append('-' + '-+-'.join(['-' * w for w in width_arr]) + '-')
        for row in self.rows:
            lines.append(' ' + ' | '.join([str(v).ljust(w) for v, w
                                           in zip(row, width_arr)]))
        return '\n'.join(lines)


@dataclass
class Figure:
    """A figure data."""
    image: Image.Image
