# expnote

_expnote_ is an experiment management tool to record facts and thoughts.

NOTE: _expnote_ is in the prototyping phase and API and data structure may change in the future.

## Installation

Python 3.8+ is required.

```shell
pip install git+https://github.com/t-hanya/expnote.git
```

## Experiment Management

**1. Initialize an expnote repository**

```shell
xn init
```

**2. Record runs**

```python
"""example.py"""
import argparse

from expnote.recording import Recorder

recorder = Recorder()

@recorder.scope
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lr', type=float, default=0.1)
    parser.add_argument('--weight-decay', type=float, default=1e-4)
    args = parser.parse_args()

    recorder.params(vars(args))  # vars(args): {'lr': 0.1, 'weight_decay': 1e-4}
    recorder.metrics({'accuracy': 0.9})

if __name__ == '__main__':
    main()
```

```shell
python example.py --lr 0.1
python example.py --lr 0.1
python example.py --lr 0.01
python example.py --lr 0.01
```

**3. Show the project status**

```shell
xn status
xn show <run id>
```

**4. Set a new experiment**

```shell
xn new "Develop a baseline model"
xn status
```

**5. Assign runs to the experiment**

```shell
xn add <run id1> [<run id2> ...] [--to <experiment id>]
xn status
```

**6. Edit experiment notes**

```shell
xn edit --purpose "Find a good baseline mdodel for image classification task."
xn edit --conclusion "ResNet18 model with lr=0.01 is a good baseline."
xn status
```

**7. Commit the experiment**

```shell
xn commit
xn status
```

**8. View past experiments**

```shell
xn log
```

## Python API

```python
from expnote.run import Run
import expnote.functions as F

runs = [
    Run(id='1', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.80}),
    Run(id='2', params={'lr': 0.5, 'wd': 0.01}, metrics={'acc': 0.82}),
    Run(id='3', params={'lr': 0.1, 'wd': 0.01}, metrics={'acc': 0.70}),
]

table = F.compare_runs(runs, grouping=False, diff_only=False)
print(table)
#>  id | lr  | wd   | acc  | comment
#> ----+-----+------+------+---------
#>  1  | 0.5 | 0.01 | 0.8  | None   
#>  2  | 0.5 | 0.01 | 0.82 | None   
#>  3  | 0.1 | 0.01 | 0.7  | None   

table = F.compare_runs(runs, grouping=True, diff_only=True)
print(table)
#>  id         | lr  | acc  | comment
#> ------------+-----+------+---------
#>  ('1', '2') | 0.5 | 0.81 | None   
#>  ('3',)     | 0.1 | 0.7  | None   
```

