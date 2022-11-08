"""
Data structures to represent the contents of an experiment notebook.
"""


import base64
from dataclasses import dataclass
import io
from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

from PIL import Image


TableValue = Union[None, int, float, str, bool, Image.Image]


TEXT_COLORS = {
    'red': {'code': '\33[31m', 'hex': '#F05555'},
    'green': {'code': '\33[32m', 'hex': '#00A24D'},
    'yellow': {'code': '\33[33m', 'hex': '#E2B914'},
}
CODE_END = '\33[0m'


@dataclass
class TableCellStyle:
    """Table cell style data."""
    text_color: Optional[Literal['red', 'green', 'yellow']] = None


@dataclass
class TableCell:
    """Table cell data."""
    value: TableValue
    style: TableCellStyle


class Table:
    """A table data structure."""

    def __init__(self,
                 columns: List[str],
                 rows: List[List[TableValue]],
                 note: Optional[str] = None,
                 title: Optional[str] = None,
                 cell_styles: Optional[List[List[dict]]] = None
                ) -> None:
        self.columns = columns
        self._data = []
        for i, row_values in enumerate(rows):
            if cell_styles is not None:
                row_styles = cell_styles[i]
            else:
                row_styles = [{} for _ in row_values]
            self._data.append([TableCell(value=value,
                                         style=TableCellStyle(**style))
                               for value, style in zip(row_values, row_styles)])
        self.title = title
        self.note = note

    @property
    def rows(self) -> List[List[TableValue]]:
        rows = []
        for row_data in self._data:
            rows.append([data.value for data in row_data])
        return rows

    def __getitem__(self, key: Tuple[int, Union[int, str]]) -> TableCell:
        """Access to table cell data with `table[row_idx, col_idx_or_name]`."""
        if not type(key) == tuple or len(key) != 2:
            raise KeyError(
                'Use `table[row_idx, col_idx_or_name]` syntax.')
        row_idx = int(key[0])
        col_idx_or_name = key[1]
        if type(col_idx_or_name) == str:
            col_idx = self.columns.index(col_idx_or_name)
        else:
            col_idx = int(col_idx_or_name)
        return self._data[row_idx][col_idx]

    def __setitem__(self,
                    key: Tuple[int, Union[int, str]],
                    value: TableValue,
                   ) -> None:
        """Set cell data with `table[row_idx, col_idx_or_name] = value`."""
        _ = int(key[0])  # type check
        col_idx_or_name = key[1]
        if type(col_idx_or_name) == str:
            name = col_idx_or_name
            if not name in self.columns:
                self.append_column(name, [None for _ in range(len(self._data))])
        self[key].value = value

    def insert_row(self, index: int, values: List[TableCell]) -> None:
        """Insert the row to the table."""
        row_data = [TableCell(value=value, style=TableCellStyle())
                    for value in values]
        self._data.insert(index, row_data)

    def append_row(self, values: List[TableCell]) -> None:
        """Append the row to the table."""
        row_data = [TableCell(value=value, style=TableCellStyle())
                    for value in values]
        self._data.append(row_data)

    def insert_column(self,
                      index: int,
                      name: str,
                      values: List[TableValue]
                     ) -> None:
        """Insert the column to the table."""
        column_data = [TableCell(value=value, style=TableCellStyle())
                       for value in values]
        self.columns.insert(index, name)
        for row_data, new_data in zip(self._data, column_data):
            row_data.insert(index, new_data)

    def append_column(self,
                      name: str,
                      values: List[TableValue]
                     ) -> None:
        """Append the column to the table."""
        column_data = [TableCell(value=value, style=TableCellStyle())
                       for value in values]
        self.columns.append(name)
        for row_data, new_data in zip(self._data, column_data):
            row_data.append(new_data)

    def _repr_html_(self) -> str:
        html = '<table>\n'
        html += '  <tr>{}</tr>\n'.format(
            ''.join([f'<th>{name}</th>' for name in self.columns]))
        for row_data in self._data:
            html += '  <tr>'
            for data in row_data:
                styles = []
                if data.style.text_color is not None:
                    styles.append('color:{}'.format(
                        TEXT_COLORS[data.style.text_color]['hex']))
                if styles:
                    style = ' style="{}"'.format(';'.join(styles))
                else:
                    style = ''
                if isinstance(data.value, Image.Image):
                    value = _to_html_img(data.value)
                else:
                    value = data.value
                html += '<td{}>{}</td>'.format(style, value)
            html += '</tr>\n'
        html += '</table>'
        return html

    def _to_markdown_table(self, pretty: bool = False) -> str:
        rows = []
        styles = []
        for row_data in self._data:
            rows.append([])
            styles.append([])
            for data in row_data:
                if isinstance(data.value, Image.Image):
                    rows[-1].append('(image)')
                else:
                    rows[-1].append(str(data.value))
                styles[-1].append(data.style)

        width_arr = []
        for i in range(len(self.columns)):
            contents = [r[i] for r in rows] + [self.columns[i]]
            max_len = max([len(str(v)) for v in contents])
            width_arr.append(max_len)

        lines = []
        lines.append('| ' + ' | '.join([col.ljust(w) for col, w
                                       in zip(self.columns, width_arr)]) + ' |')
        lines.append('|-' + '-|-'.join(['-' * w for w in width_arr]) + '-|')
        for row, row_style in zip(rows, styles):
            line_elems = []
            for value, style, width in zip(row, row_style, width_arr):
                text = value.ljust(width)
                if pretty and style.text_color is not None:
                    text = TEXT_COLORS[style.text_color]['code'] + text + CODE_END
                line_elems.append(text)
            lines.append('| ' + ' | '.join([text for text in line_elems]) + ' |')
        content = '\n'.join(lines)

        # title & note
        if self.title is not None:
            content = f'## {self.title}\n\n' + content
        if self.note is not None:
            content = content + '\n\n' + self.note
        return content

    def _repr_pretty_(self, *args) -> str:
        return self._to_markdown_table(pretty=True)

    def _repr_markdown_(self) -> str:
        return self._to_markdown_table()

    def __str__(self) -> str:
        return self._repr_markdown_()


def _to_html_img(image: Image.Image,
                 max_width: int = 150,
                 max_height: int = 100) -> str:
    if (image.height / image.width) > (max_height / max_width):
        if image.height > max_height:
            width = int(round(image.width * max_height / image.height))
            height = max_height
            image = image.resize((width, height), resample=Image.BILINEAR)
    else:
        if image.width > max_width:
            height = int(round(image.height * max_width / image.width))
            width = max_width
            image = image.resize((width, height), resample=Image.BILINEAR)

    buffer = io.BytesIO()
    image.save(buffer, 'png')
    base64_image = base64.b64encode(buffer.getvalue()).decode("ascii")
    return '<img src="data:image/png;base64,{}">'.format(base64_image)


@dataclass
class Figure:
    """A figure data."""
    image: Image.Image
    note: Optional[str] = None
    title: Optional[str] = None

    def __str__(self) -> str:
        content = 'Figure(title="{}"'.format(self.title)
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
