"""
Utility functions for visualization.
"""


from functools import reduce
import io
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import matplotlib.pyplot as plt
from PIL import Image

from expnote.run import Run
from expnote.run import RunGroup
from expnote.note import Figure


DEFAULT_STEP_KEYS = ('epoch', 'epochs',
                     'step', 'steps',
                     'iteration', 'iterations', 'iter')
DEFAULT_SUBSETS = {
    'train': ('train', 'training'),
    'val': ('val', 'validation'),
    'test': ('test',),
    'eval': ('eval', 'evaluation'),
}
DEFAULT_SUBSET_SEPARATOR = ('/', '_', '-', ':')


def _determine_step_key(step_metrics_list: List[List[dict]]
                       ) -> Optional[str]:
    """Determine appropriate step name from step metrics data."""

    keyset_list = [set(sm[0].keys()) for sm in step_metrics_list]
    common_keys = reduce(lambda s1, s2: s1 & s2, keyset_list)

    # find an available step key
    for step_key_candidate in DEFAULT_STEP_KEYS:
        if step_key_candidate in common_keys:
            return step_key_candidate

    # index in step_metrics (this is a list) will be used
    return None


def _split_subset_name(metric_name: str) -> Tuple[Optional[str], str]:
    """Split metric name into subset name and rest if subset name is found."""
    split_patterns = {}
    for sep in DEFAULT_SUBSET_SEPARATOR:
        blocks = metric_name.split(sep)
        if len(blocks) > 1:
            # ex) train_class_loss -> {'train': 'class_loss'}
            split_patterns[blocks[0]] = sep.join(blocks[1:])
            # ex) acc_val -> {'val': 'acc'}
            split_patterns[blocks[-1]] = sep.join(blocks[:-1])

    for label, candidates in DEFAULT_SUBSETS.items():
        for candidate in candidates:
            if candidate in split_patterns:
                return (label, split_patterns[candidate])

    # cannot find subset name -> do not split
    return (None, metric_name)


def _list_step_metrics(step_metrics_list: List[List[dict]],
                       compare_subsets: bool = False,
                      ) -> List[Union[str, dict]]:
    """List all step metrics.

    Step keys (like epochs, steps) are ignored.
    """
    metric_name_to_subsets = {}
    for step_metrics in step_metrics_list:
        for metric_name in step_metrics[0].keys():
            if metric_name in DEFAULT_STEP_KEYS:
                continue
            if compare_subsets:
                subset, rest_name = _split_subset_name(metric_name)
            else:
                subset = None
                rest_name = metric_name

            if not rest_name in metric_name_to_subsets:
                metric_name_to_subsets[rest_name] = {}
            metric_name_to_subsets[rest_name][subset] = metric_name

    ret = []
    for v in metric_name_to_subsets.values():
        if len(v) == 1 and None in v:
            ret.append(v.pop(None))
        else:
            ret.append(v)
    return ret


def visualize_step_metrics(runs: List[Union[Run, RunGroup]],
                           compare_subsets: bool = True,
                           ncols: int = 2
                          ) -> Figure:
    """Visualize step metrics."""
    runs = [run for run in runs if run.step_metrics is not None]
    if not runs:
        raise ValueError('No run data with step metrics data.')

    step_key = _determine_step_key([run.step_metrics for run in runs])
    metric_keys = _list_step_metrics([run.step_metrics for run in runs],
                                     compare_subsets=compare_subsets)

    nrows = len(metric_keys) // ncols
    if len(metric_keys) % ncols != 0:
        nrows += 1

    fig, axes = plt.subplots(ncols=ncols,
                             nrows=nrows,
                             figsize=(ncols * 6, nrows * 3),
                             squeeze=False)

    color_map = plt.get_cmap('tab10')
    line_styles = {'train': '--', 'val': '-', 'test': '-.', 'eval': '-.'}

    for run_idx, run in enumerate(runs):
        steps = [d[step_key] for d in run.step_metrics]
        color = color_map(run_idx)

        for i in range(nrows):
            for j in range(ncols):
                idx = i * ncols + j
                if idx >= len(metric_keys):
                    if run_idx == 0:
                        axes[i, j].set_xticks([])
                        axes[i, j].set_yticks([])
                    continue

                metric_key = metric_keys[idx]
                if type(metric_key) == dict:
                    for subset, metric_name in metric_key.items():
                        if run_idx == 0:
                            _, common_name = _split_subset_name(metric_name)
                            axes[i, j].set_title(common_name)

                        if not metric_name in run.step_metrics[0]:
                            continue
                        values = [d[metric_name] for d in run.step_metrics]
                        axes[i, j].plot(steps,
                                        values,
                                        line_styles[subset],
                                        color=color,
                                        label='{:6}({})'.format(run.id, subset))
                        axes[i, j].legend()
                else:
                    if run_idx == 0:
                        axes[i, j].set_title(metric_key)
                    values = [d[metric_key] for d in run.step_metrics]
                    axes[i, j].plot(steps,
                                    values,
                                    '-',
                                    color=color,
                                    label='{:6}'.format(run.id))

    for i in range(nrows):
        for j in range(ncols):
            idx = i * ncols + j
            if (i * ncols + j) < len(metric_keys):
                axes[i, j].legend()

    # to image object
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    image = Image.open(buf)
    plt.close()

    return Figure(image=image)
