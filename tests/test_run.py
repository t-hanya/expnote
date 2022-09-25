from expnote.run import Run
from expnote.run import RunGroup


class TestRun:

    def test(self):
        run = Run(id='0', params={'lr': 0.5}, metrics={'acc': 0.9})
        assert run.id == '0'
        assert run.params == {'lr': 0.5}
        assert run.metrics == {'acc': 0.9}


class TestRunGroup:

    def test(self):
        run1 = Run(id='0', params={'lr': 0.5}, metrics={'acc': 0.9})
        run2 = Run(id='1', params={'lr': 0.5}, metrics={'acc': 0.8})
        group = RunGroup([run1, run2],
                         id=('0', '1'),
                         params={'lr': 0.5},
                         metrics={'acc': 0.85})

        assert group.id == ('0', '1')
        assert group.params == {'lr': 0.5}  # common param
        assert group.metrics == {'acc': 0.85}  # averaged
