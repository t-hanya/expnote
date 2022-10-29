"""
Entry point for CLI.
"""


from argparse import ArgumentParser
from argparse import Namespace
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from expnote.cli.commands import InitCmd
from expnote.cli.commands import NewCmd
from expnote.cli.commands import AddCmd
from expnote.cli.commands import StatusCmd
from expnote.cli.commands import ResetCmd
from expnote.cli.commands import RmCmd
from expnote.cli.commands import ShowCmd
from expnote.cli.commands import CommitCmd
from expnote.cli.commands import LogCmd
from expnote.cli.commands import EditCmd


COMMANDS = [
    ('init', InitCmd),
    ('new', NewCmd),
    ('add', AddCmd),
    ('status', StatusCmd),
    ('reset', ResetCmd),
    ('rm', RmCmd),
    ('show', ShowCmd),
    ('commit', CommitCmd),
    ('log', LogCmd),
    ('edit', EditCmd),
]


class Command:
    """Interface definition of command class."""

    def __init__(self, parser: ArgumentParser):
        """Define arguments."""
        raise NotImplementedError()

    def __call__(self, args: Namespace):
        """Execute main task of the command."""
        raise NotImplementedError()


class SubcommandExecutor:
    """Subcommand executor."""

    def __init__(self, commands: List[Tuple[str, Type[Command]]]) -> None:
        self.parser = ArgumentParser()
        self.commands = {}

        subparsers = self.parser.add_subparsers(dest='subcommand')
        for cmd_name, cmd_class in commands:
            subparser = subparsers.add_parser(cmd_name)
            self.commands[cmd_name] = cmd_class(subparser)

    def __call__(self, args: Optional[str] = None) -> None:
        """Execute subcommands."""
        args = self.parser.parse_args(args=args)
        if args.subcommand is not None:
            self.commands[args.subcommand](args)
        else:
            self.parser.print_help()


def main():
    """Entry point of CLI."""
    SubcommandExecutor(COMMANDS)()


if __name__ == '__main__':
    main()
