# expnote

_expnote_ is an experiment management tool to record facts and thoughts.

## Usage

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
