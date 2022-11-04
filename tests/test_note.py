from PIL import Image

from expnote.note import Table
from expnote.note import Figure
from expnote.note import Note


class TestTable:

    def test(self):
        table = Table(
            columns=['a', 'b', 'c'],
            rows=[[1, 10, 100],
                  [2, 20, 200],
                  [3, 30, 300]]
        )
        assert table.columns == ['a', 'b', 'c']
        assert table.rows[0] == [1, 10, 100]
        assert table.rows[1] == [2, 20, 200]
        assert table.rows[2] == [3, 30, 300]

        assert len(str(table).splitlines()) == 5

    def test_note(self):
        table = Table(
            columns=['a', 'b', 'c'],
            rows=[[1, 10, 100],
                  [2, 20, 200],
                  [3, 30, 300]]
        )
        table.note = "note"
        table.title = "title"

        assert "note" in str(table)
        assert "title" in str(table)

    def test_set(self):
        table = Table(
            columns=['a', 'b', 'c'],
            rows=[[1, 10, 100],
                  [2, 20, 200],
                  [3, 30, 300]]
        )
        table[0, 0].value = 9
        table[0, 'b'].value = 90
        table[0, 'c'] = 900
        table[0, 'c'].style.text_color = 'red'

        assert table.rows[0][0] == 9
        assert table.rows[0][1] == 90
        assert table.rows[0][2] == 900

    def test_row_operation(self):
        table = Table(
            columns=['a', 'b', 'c'],
            rows=[[1, 10, 100],
                  [3, 30, 300],
                  [4, 40, 400]]
        )
        table.insert_row(1, [2, 20, 200])
        table.append_row([5, 50, 500])
        assert table.rows == [[1, 10, 100],
                              [2, 20, 200],
                              [3, 30, 300],
                              [4, 40, 400],
                              [5, 50, 500]]

    def test_column_operation(self):
        table = Table(
            columns=['a', 'c', 'd'],
            rows=[[1, 100, 1000],
                  [2, 200, 2000],
                  [3, 300, 3000]]
        )
        table.insert_column(1, 'b', [10, 20, 30])
        table.append_column('e', [10000, 20000, 30000])
        assert table.columns == ['a', 'b', 'c', 'd', 'e']
        assert table.rows == [[1, 10, 100, 1000, 10000],
                              [2, 20, 200, 2000, 20000],
                              [3, 30, 300, 3000, 30000]]

    def test_auto_add_column(self):
        table = Table(
            columns=['a', 'b', 'c'],
            rows=[[1, 10, 100],
                  [2, 20, 200],
                  [3, 30, 300]]
        )
        table[0, 'comment'] = 'A comment'
        assert table.rows[0][3] == 'A comment'
        assert table.rows[1][3] is None
        assert table.rows[2][3] is None

    def test_repr_html(self):
        table = Table(
            columns=['a', 'b', 'c', 'd', 'e'],
            rows=[[1, 10., True, 'some text', Image.new('RGB', (20, 10))],
                  [None, None, None, None, None]],
        )
        html = table._repr_html_()
        assert 'some text' in html

    def test_repr_pretty(self):
        table = Table(
            columns=['a', 'b', 'c', 'd', 'e'],
            rows=[[1, 10., True, 'some text', Image.new('RGB', (20, 10))],
                  [None, None, None, None, None]],
        )
        text = table._repr_pretty_()
        assert 'some text' in text

    def test_repr_markdown(self):
        table = Table(
            columns=['a', 'b', 'c', 'd', 'e'],
            rows=[[1, 10., True, 'some text', Image.new('RGB', (20, 10))],
                  [None, None, None, None, None]],
        )
        md_text = table._repr_markdown_()
        assert 'some text' in md_text


class TestFigure:

    def test(self):
        fig = Figure(
            image=Image.new('RGB', (100, 50))
        )
        assert fig.image.size == (100, 50)

    def test_note(self):
        fig = Figure(
            image=Image.new('RGB', (100, 50))
        )
        fig.note = "note"
        fig.title = "title"

        assert "note" in str(fig)
        assert "title" in str(fig)


class TestNote:
    def test(self):
        note = Note(
            title='title',
            note='note'
        )
        assert 'title' in str(note)
        assert 'note' in str(note)
