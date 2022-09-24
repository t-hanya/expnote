from expnote.run import Run


class TestRun:

    def test(self):
        run = Run(id='0', params={'lr': 0.5}, metrics={'acc': 0.9})
        assert run.id == '0'
        assert run.params == {'lr': 0.5}
        assert run.metrics == {'acc': 0.9}
