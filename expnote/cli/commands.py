"""
Define subcommands for expnote CLI.
"""


from argparse import ArgumentParser
from argparse import Namespace
from dataclasses import asdict
import json
import os
import sys

from expnote.note import Table
from expnote.experiment import Experiment
from expnote.repository import Repository
from expnote.functions import compare_runs


class InitCmd:
    """Initialize a repository."""

    def __init__(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> None:
        try:
            Repository()
        except FileNotFoundError:
            Repository.initialize()
            msg = 'Successfully initialized in {}/.expnote'.format(
                os.getcwd())
            print(msg)
        else:
            msg = 'Already exists in {}/.expnote'.format(os.getcwd())
            print(msg)


def _get_repo() -> Repository:
    """Get the repository instance.

    If not exists, print a message and exit.
    """
    try:
        repo = Repository()
    except FileNotFoundError:
        print('No expnote repository found.')
        print('Please create a repo with `expnote init` command.')
        sys.exit()
    return repo


class NewCmd:
    """Set a new experiment."""

    def __init__(self, parser: ArgumentParser) -> None:
        parser.add_argument('title', type=str,
                            help='The title of the new experiment')
        parser.add_argument('--purpose', '-p', type=str,
                            default=None,
                            help='The purpose of the experiment')

    def __call__(self, args: Namespace) -> None:
        repo = _get_repo()
        exp = Experiment(title=args.title, purpose=args.purpose)
        with repo.open_workspace() as workspace:
            exp = repo.save_experiment(exp)
            workspace.add_uncommitted_experiment(exp.id)

        print('Add a new experiment (id={}, title="{}")'.format(
            exp.id, exp.title))


class AddCmd:
    """Assign runs to experiments."""

    def __init__(self, parser: ArgumentParser) -> None:
        parser.add_argument('run_ids', type=str, nargs='+',
                            help='Run IDs to be added to the experiment.')
        parser.add_argument('--to', type=str, default=None,
                            help='The experiment ID to add the runs.')

    def __call__(self, args: Namespace) -> None:
        # check the run ids exist.
        repo = _get_repo()
        full_run_ids = []
        for run_id in args.run_ids:
            found = repo.find_runs(run_id)
            if not found:
                print('No run record found for the id: {}'.format(run_id))
                return

            elif len(found) > 1:
                print('Multiple runs are found for the id: {}'.format(run_id))
                for i, run in enumerate(found):
                    print('{}: {}'.format(i + 1, run))
                return
            full_run_ids.append(found[0].id)

        with repo.open_workspace() as workspace:

            # determine target experiment
            if not workspace.uncommitted_experiments:
                print('No uncommitted experiment found.')
                print('Use `new` command to add a new experiment.')
                return

            if args.to is None:
                if len(workspace.uncommitted_experiments) > 1:
                    print('Multiple uncommitted experiments are found.')
                    print('Specify the target experiment via `--to` option.')
                    return
                else:
                    exp_id = workspace.uncommitted_experiments[0]
            else:
                if args.to in workspace.uncommitted_experiments:
                    exp_id = args.to
                else:
                    msg = 'No uncommitted experiment with the id: {}'.format(
                        args.to)
                    print(msg)
                    return

            # assign runs to the experiment
            for run_id in full_run_ids:
                workspace.assign_run_to_experiment(run_id, exp_id)


class StatusCmd:
    """Display the project status."""

    def __init__(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> None:
        repo = _get_repo()

        with repo.open_workspace() as ws:
            untracked_run_ids = ws.untracked_runs
            uncommitted_experiment_ids = ws.uncommitted_experiments
            assigned_runs = ws.assigned_runs

        untracked_runs = [repo.get_run(run_id)
                          for run_id in untracked_run_ids]
        experiments = [repo.get_experiment(exp_id)
                       for exp_id in uncommitted_experiment_ids]
        for exp in experiments:
            print('\n{} (id={}):\n'.format(exp.title, exp.id))
            run_ids = assigned_runs[exp.id]
            runs = [repo.get_run(run_id) for run_id in run_ids]
            print(compare_runs(runs, grouping=False))

        if untracked_runs:
            print('\nUntracked runs:\n')
            print(compare_runs(untracked_runs, grouping=False))
        print('')


class ResetCmd:
    """Reset run-to-experiment assignments in workspace."""

    def __init__(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> None:
        with _get_repo().open_workspace() as workspace:
            workspace.reset_assignments()


class RmCmd:
    """Remove run from untracked run list."""

    def __init__(self, parser: ArgumentParser) -> None:
        parser.add_argument('run_ids', type=str, nargs='+',
                            help='Run IDs to be removed from workspace.')

    def __call__(self, args: Namespace) -> None:
        repo = _get_repo()
        full_run_ids = []
        for run_id in args.run_ids:
            found = repo.find_runs(run_id)
            if not found:
                print('No run record found for the id: {}'.format(run_id))
                return
            elif len(found) > 1:
                print('Multiple runs are found for the id: {}'.format(run_id))
                for i, run in enumerate(found):
                    print('{}: {}'.format(i + 1, run))
                return
            full_run_ids.append(found[0].id)

        with repo.open_workspace() as workspace:
            for run_id in full_run_ids:
                try:
                    workspace.remove_run(run_id)
                except KeyError as e:
                    pass


class ShowCmd:
    """Display the run info."""

    def __init__(self, parser: ArgumentParser) -> None:
        parser.add_argument('run_id', type=str, help='Run ID to be displayed.')

    def __call__(self, args: Namespace) -> None:
        repo = _get_repo()
        found = repo.find_runs(args.run_id)
        if not found:
            print('No run record found for the id: {}'.format(args.run_id))
        elif len(found) > 1:
            print('Multiple runs are found for the id: {}'.format(args.run_id))
            for i, run in enumerate(found):
                print('{}: {}'.format(i + 1, run))
        else:
            print(json.dumps(asdict(found[0]), indent=2))



class CommitCmd:
    """Commit and log an experiment."""

    def __init__(self, parser: ArgumentParser) -> None:
        parser.add_argument('--id', type=str, default=None,
                            help='Target experiment ID to be committed.')
        parser.add_argument('--conclusion', type=str, default=None,
                            help=('A conclusion of the experiment. '
                                  'If the conclusion field of the experiment '
                                  'is empty, this should be specified.'))

    def __call__(self, args: Namespace) -> None:

        repo = _get_repo()
        with repo.open_workspace() as workspace:

            # determine target experiment
            if not workspace.uncommitted_experiments:
                print('No uncommitted experiment found.')
                print('Use `new` command to add a new experiment.')
                return

            if args.id is None:
                if len(workspace.uncommitted_experiments) > 1:
                    print('Multiple uncommitted experiments are found.')
                    print('Specify the target experiment via `--id` option.')
                    return
                else:
                    exp_id = workspace.uncommitted_experiments[0]
            else:
                if args.to in workspace.uncommitted_experiments:
                    exp_id = args.to
                else:
                    msg = 'No uncommitted experiment with the id: {}'.format(
                        args.to)
                    return

            # commit operation
            exp = repo.get_experiment(exp_id)
            if exp.run_ids is None:
                exp.run_ids = workspace.assigned_runs[exp_id]

            if exp.notes is None:
                exp.notes = []

            has_table = any([type(note) == Table for note in exp.notes])
            if not has_table and len(exp.run_ids) > 0:
                runs = [repo.get_run(run_id) for run_id in exp.run_ids]
                exp.notes.insert(0, compare_runs(runs))

            if args.conclusion is not None:
                exp.conclusion = args.conclusion

            repo.save_experiment(exp)
            workspace.commit(exp.id)


class LogCmd:
    """Show already committed experiments."""

    def __init__(self, parser: ArgumentParser) -> None:
        parser.add_argument('--num', '-n', type=int, default=None,
                            help='Maximum number of experiments to be displayed.')

    def __call__(self, args: Namespace) -> None:
        repo = _get_repo()
        with repo.open_workspace() as workspace:
            uncommitted_ids = workspace.uncommitted_experiments

        if args.num is None:
            limit = None
        else:
            limit = len(uncommitted_ids) + args.num

        experiments = repo.find_experiments(limit=limit, reverse=True)
        experiments = [e for e in experiments if not e.id in uncommitted_ids]
        if limit is not None:
            experiments = experiments[:limit]

        print('\n\n'.join([str(e) for e in experiments]))
