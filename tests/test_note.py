from PIL import Image

from expnote.note import Table
from expnote.note import Figure


class TestNote:

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


class TestFigure:

    def test(self):
        fig = Figure(
            image=Image.new('RGB', (100, 50))
        )
        assert fig.image.size == (100, 50)
