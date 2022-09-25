import math

from expnote.run import Run
from expnote.functions.comparison import make_run_groups
from expnote.functions.comparison import compare_runs


class TestMakeRunGroups:

    def test(self):
        run1 = Run(id='1', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.80})
        run2 = Run(id='2', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.82})
        run3 = Run(id='3', params={'lr': 0.1, 'wd': 0.01}, metrics={'acc': 0.70})

        groups = make_run_groups([run1, run2, run3])

        assert len(groups) == 2

        assert groups[0].id == ('1', '2')
        assert groups[0].params == {'lr': 0.5, 'wd': 0.01}
        assert math.isclose(groups[0].metrics['acc'], 0.81)

        assert groups[1].id == ('3',)
        assert groups[1].params == {'lr': 0.1, 'wd': 0.01}
        assert math.isclose(groups[1].metrics['acc'], 0.70)


class TestCompareRuns:

    def test(self):
        run1 = Run(id='1', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.80})
        run2 = Run(id='2', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.82})
        run3 = Run(id='3', params={'lr': 0.1, 'wd': 0.01}, metrics={'acc': 0.70})

        table = compare_runs([run1, run2, run3])
        assert len(table.rows) == 2
        assert set(table.columns) == set(['id', 'lr', 'acc', 'comment'])

    def test_not_only_diff(self):
        run1 = Run(id='1', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.80})
        run2 = Run(id='2', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.82})
        run3 = Run(id='3', params={'lr': 0.1, 'wd': 0.01}, metrics={'acc': 0.70})

        table = compare_runs([run1, run2, run3], diff_only=False)
        assert set(table.columns) == set(['id', 'lr', 'wd', 'acc', 'comment'])
        assert len(table.rows) == 2

    def test_not_grouping(self):
        run1 = Run(id='1', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.80})
        run2 = Run(id='2', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.82})
        run3 = Run(id='3', params={'lr': 0.1, 'wd': 0.01}, metrics={'acc': 0.70})

        table = compare_runs([run1, run2, run3], grouping=False)
        assert set(table.columns) == set(['id', 'lr', 'acc', 'comment'])
        assert len(table.rows) == 3
