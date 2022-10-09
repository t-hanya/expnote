import pytest

from expnote.recording.memory import Memory
from expnote.recording.collectors import RunInfoCollector


class TestRunInfoCollector:

    def test(self):
        with Memory(run_id='1') as mem:
            collector = RunInfoCollector()
            with collector:
                pass

        assert 'start_time' in mem.info
        assert 'end_time' in mem.info
        assert 'status' in mem.info

    @pytest.mark.parametrize('exc_type, expected', [
        (None, 'complete'),
        (KeyboardInterrupt, 'interrupted'),
        (Exception, 'failed'),
    ])
    def test_status(self, exc_type, expected):
        try:
            with Memory(run_id='1') as mem:
                collector = RunInfoCollector()
                with collector:
                    if exc_type is not None:
                        raise exc_type

        except exc_type:
            pass

        assert mem.info['status'] == expected
