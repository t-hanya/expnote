from expnote.recording import Recorder


class Repository:

    def __init__(self):
        self.runs = {}

    def save_run(self, run):
        self.runs[run.id] = run

    def find_runs(self):
        return list(self.runs.values())


class TestRecorder:
    def test(self):

        repo = Repository()

        recorder = Recorder(
            repo=repo
        )

        @recorder.scope
        def main():
            recorder.params({'lr': 0.1})
            recorder.metrics({'acc': 0.9})
            for i in range(5):
                recorder.metrics({'loss': 5 - i}, step=(i, 'epoch'))

        main()

        runs = repo.find_runs()
        assert len(runs) == 1

        run = runs[0]
        assert run.params == {'lr': 0.1}
        assert run.metrics == {'acc': 0.9}
        assert run.step_metrics == [
            {'epoch': 0, 'loss': 5},
            {'epoch': 1, 'loss': 4},
            {'epoch': 2, 'loss': 3},
            {'epoch': 3, 'loss': 2},
            {'epoch': 4, 'loss': 1}
        ]
        assert 'start_time' in run.info
        assert 'end_time' in run.info
        assert run.info['status'] == 'complete'

