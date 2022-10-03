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

    def test_step_metrics(self):
        run1 = Run(id='1', params={'lr': 0.5}, metrics={}, step_metrics=[
            {'epoch': 0, 'acc': 0.5, 'loss': 10, 'lr': 0.1},
            {'epoch': 1, 'acc': 0.5, 'loss': 10, 'lr': 0.1},
        ])
        run2 = Run(id='2', params={'lr': 0.5}, metrics={}, step_metrics=[
            {'epoch': 1, 'acc': 0.7, 'loss': 12},
            {'epoch': 2, 'acc': 0.7, 'loss': 12},
        ])
        group = make_run_groups([run1, run2])[0]
        expected_step_metrics = [
            {'epoch': 0, 'acc': 0.5, 'loss': 10},
            {'epoch': 1, 'acc': 0.6, 'loss': 11},
            {'epoch': 2, 'acc': 0.7, 'loss': 12},
        ]
        assert len(group.step_metrics) == len(expected_step_metrics)
        for step_metric, expected in zip(group.step_metrics, expected_step_metrics):
            assert step_metric['epoch'] == expected['epoch']
            assert math.isclose(step_metric['acc'], expected['acc'])
            assert math.isclose(step_metric['loss'], expected['loss'])


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
