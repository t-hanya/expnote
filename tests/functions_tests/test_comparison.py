import math

from expnote.run import Run
from expnote.functions.comparison import make_run_groups


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
