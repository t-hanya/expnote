import pytest

from expnote.recording.memory import merge_dicts
from expnote.recording.memory import Memory
from expnote.recording.memory import set_params
from expnote.recording.memory import set_metrics


@pytest.mark.parametrize('dict1, dict2, expected', [
    # flat
    ({'a': 1}, {'b': 2}, {'a': 1, 'b': 2}),
    # nested
    ({'a': {'b': 1}}, {'a': {'c': 2}}, {'a': {'b': 1, 'c': 2}}),
    # update (dict2 is prioritized)
    ({'a': 1}, {'a': {'b': 1}}, {'a': {'b': 1}}),
    ({'a': {'b': 1}}, {'a': {'b': 2}}, {'a': {'b': 2}}),
])
def test_merge_dicts(dict1, dict2, expected):
    assert merge_dicts(dict1, dict2) == expected


class Repository:
    """Simple repository implementation for testing."""

    def __init__(self):
        self.runs = {}

    def save_run(self, run):
        self.runs[run.id] = run

    def get_run(self, run_id):
        return self.runs[run_id]


class TestMemory:

    def test(self):
        repo = Repository()

        with Memory(run_id='0', repo=repo) as mem:

            # params
            mem.set_params({'lr': 0.1})
            set_params({'model': {'backbone': 'resnet18'}})
            set_params({'model': {'image_size': (224, 224)}})

            # metrics
            mem.set_metrics({'acc': 0.9})
            set_metrics({'mae': 10.})

            # step metrics
            for i in range(3):
                mem.set_metrics({'loss': 5 - i}, step=(i, 'epoch'))
            for i in range(3, 5):
                set_metrics({'loss': 5 - i}, step=(i, 'epoch'))

            # save
            mem.flush()

        run = repo.get_run('0')
        assert run.id == '0'
        assert run.params == {
            'lr': 0.1,
            'model': {
                'backbone': 'resnet18',
                'image_size': (224, 224)
            }
        }
        assert run.metrics == {
            'acc': 0.9,
            'mae': 10.
        }
        assert run.step_metrics == [
            {'epoch': 0, 'loss': 5},
            {'epoch': 1, 'loss': 4},
            {'epoch': 2, 'loss': 3},
            {'epoch': 3, 'loss': 2},
            {'epoch': 4, 'loss': 1},
        ]
