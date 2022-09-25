"""
Implement functions to compare runs.
"""


import copy
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from expnote.run import Run
from expnote.run import RunGroup
from expnote.note import Table


def make_run_groups(runs: List[Run]) -> List[RunGroup]:
    """Compare run params and organize them into multiple run groups."""

    # make groups
    groups = []
    for run in runs:
        for group in groups:
            if run.params == group[0].params:
                group.append(run)
                break
        else:
            groups.append([run])

    # convert into RunGroup objects.
    ret = []
    for group in groups:

        # compute averaged metrics
        metric_values = {}
        for run in group:
            for key, value in run.metrics.items():
                if not key in metric_values:
                    metric_values[key] = []
                metric_values[key].append(value)
        averaged_metrics = {}
        for key, values in metric_values.items():
            if len(values) > 1:
                averaged_metrics[key] = sum(values) / len(values)
            else:
                averaged_metrics[key] = values[0]

        ret.append(RunGroup(
            runs=group,
            id=tuple(run.id for run in group),
            params=copy.deepcopy(group[0].params),
            metrics=averaged_metrics
        ))

    return ret


def _list_key_values(data: dict,
                     scope: Optional[Tuple[str, ...]] = None
                    ) -> List[Tuple[str, Any]]:
    """Get a flat (key, value) list from the possibly nested dict."""
    scope = scope or tuple()
    key_values = []
    for key, value in data.items():
        full_key = scope + (key,)
        if type(value) == dict:
            key_values += _list_key_values(value, scope=full_key)
        else:
            key_values.append((full_key, value))
    return key_values


def _get_value(data: dict, key_path: Tuple[str, ...]) -> Any:
    """Get a value from the dict using the key path."""
    for elem in key_path:
        if not elem in data:
            return None
        data = data[elem]
    return data


def compare_runs(runs: List[Run],
                 grouping: bool = True,
                 diff_only: bool = True
                ) -> Table:
    """Compare runs and return as a table data."""
    if grouping:
        runs = make_run_groups(runs)

    param_variations = {}
    metric_values = {}
    for run in runs:
        for key_path, value in _list_key_values(run.params):
            if not key_path in param_variations:
                param_variations[key_path] = set()
            param_variations[key_path].add(value)
        for key_path, value in _list_key_values(run.metrics):
            if not key_path in metric_values:
                metric_values[key_path] = []
            metric_values[key_path].append(value)

    if diff_only:
        param_variations = {k: v for k, v in param_variations.items()
                            if len(v) > 1}

    param_keys = tuple(param_variations.keys())
    metric_keys = tuple(metric_values.keys())

    columns = ['id']
    columns += ['.'.join(kp) for kp in param_keys]
    columns += ['.'.join(kp) for kp in metric_keys]
    columns += ['comment']

    rows = []
    for run in runs:
        row = [str(run.id)]
        row += [_get_value(run.params, kp) for kp in param_keys]
        row += [_get_value(run.metrics, kp) for kp in metric_keys]
        row += [None]
        rows.append(row)

    return Table(columns=columns, rows=rows)
