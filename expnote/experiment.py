"""
Define an experiment object to organize facts and thoughts.
"""


from typing import List
from typing import Optional
from typing import Union

from expnote.note import Note
from expnote.note import Figure
from expnote.note import Table


Content = Union[Note, Figure, Table]


class Experiment:
    """An experiment object to organize facts and thoughts."""

    def __init__(self,
                 title: str,
                 purpose: Optional[str] = None,
                 conclusion: Optional[str] = None,
                 notes: Optional[List[Content]] = None,
                 id: Optional[str] = None,
                 run_ids: Optional[List[str]] = None,
                ) -> None:
        self.title = title
        self.purpose = purpose
        self.conclusion = conclusion
        self.notes = notes

        self.id = id
        self.run_ids = run_ids

    def add(self, content: Content) -> None:
        if self.notes is None:
            self.notes = []
        self.notes.append(content)

    def __str__(self) -> str:
        content = f'# {self.title}'
        if self.purpose is not None:
            content += f'\n\nPurpose: {self.purpose}'
        if self.purpose is not None:
            content += f'\n\nConclusion: {self.conclusion}'
        if self.notes is not None:
            note_contents = [str(note) for note in self.notes]
            content += '\n\n' + '\n\n'.join(note_contents)
        return content
