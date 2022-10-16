from expnote.experiment import Experiment
from expnote.note import Note


class TestExperiment:

    def test(self):
        exp = Experiment(title='title')
        exp.add(Note('content'))

        assert 'title' in str(exp)
        assert 'content' in str(exp)
