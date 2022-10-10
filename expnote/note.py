"""
Data structures to represent the contents of an experiment notebook.
"""


from dataclasses import dataclass
from typing import List
from typing import Any
from typing import Optional

from PIL import Image


@dataclass
class Table:
    """A table data structure."""
    columns: List[str]
    rows: List[List[Any]]
    note: Optional[str] = None
    title: Optional[str] = None

    def __str__(self) -> str:
        # table
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
        content = '\n'.join(lines)

        # title & note
        if self.title is not None:
            content = f'## {self.title}\n\n' + content
        if self.note is not None:
            content = content + '\n\n' + self.note
        return content


@dataclass
class Figure:
    """A figure data."""
    image: Image.Image
    alt: Optional[str] = None
    file_name: Optional[str] = None
    note: Optional[str] = None
    title: Optional[str] = None

    def __str__(self) -> str:
        content = '<Figure file_name="{}" alt="{}">'.format(
            self.file_name,
            self.alt
        )
        # title & note
        if self.title is not None:
            content = f'## {self.title}\n\n' + content
        if self.note is not None:
            content = content + '\n\n' + self.note
        return content


@dataclass
class Note:
    """A note data."""
    note: str
    title: Optional[str] = None

    def __str__(self) -> str:
        content = self.note
        if self.title is not None:
            content = f'## {self.title}\n\n' + content
        return content
