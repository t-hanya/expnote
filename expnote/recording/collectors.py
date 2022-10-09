"""
Helper objects to collect run metadata.
"""


import datetime

from expnote.recording.memory import set_info


TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class RunInfoCollector:
    """Basic run info collector."""

    def __enter__(self) -> 'RunInfoCollector':
        now = datetime.datetime.now()
        set_info({'start_time': now.strftime(TIMESTAMP_FORMAT),
                  'end_time': None,
                  'status': 'running'})
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        now = datetime.datetime.now()
        if exc_value is None:
            status = 'complete'
        elif exc_type == KeyboardInterrupt:
            status = 'interrupted'
        else:
            status = 'failed'
        set_info({'end_time': now.strftime(TIMESTAMP_FORMAT),
                  'status': status})
