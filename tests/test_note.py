from expnote.note import Table


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
