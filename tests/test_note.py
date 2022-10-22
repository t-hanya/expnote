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
