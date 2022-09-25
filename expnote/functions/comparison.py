"""
Implement functions to compare runs.
"""


import copy
from typing import List

from expnote.run import Run
from expnote.run import RunGroup


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
