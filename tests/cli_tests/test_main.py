import pytest

from expnote.cli.main import SubcommandExecutor


class DummyCommand:

    def __init__(self, parser):
        parser.add_argument('value')

    def __call__(self, args):
        if args.value == 'errorvalue':
            raise ValueError()


class TestSubcommandExecutor:

    def test_command(self):
        executor = SubcommandExecutor([
            ('dummy', DummyCommand),
        ])
        executor(args=['dummy', 'value'])
        with pytest.raises(ValueError):
            executor(args=['dummy', 'errorvalue'])
