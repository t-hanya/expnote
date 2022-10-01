from PIL import Image
import pytest

from expnote.run import Run
from expnote.functions.visualization import _determine_step_key
from expnote.functions.visualization import _split_subset_name
from expnote.functions.visualization import _list_step_metrics
from expnote.functions import visualize_step_metrics


class TestDetermineStepKey:

    def test_normal(self):
        step_metrics_list = [
            [{'epoch': 0}, {'epoch': 1}],
            [{'epoch': 0}],
        ]
        ret = _determine_step_key(step_metrics_list)
        assert ret == 'epoch'

    def test_common_key(self):
        step_metrics_list = [
            [{'epoch': 0, 'iteration': 100}],
            [{'iteration': 100}],
        ]
        ret = _determine_step_key(step_metrics_list)
        assert ret == 'iteration'

    def test_no_available_key(self):
        step_metrics_list = [
            [{'loss': 10}],
            [{'loss': 20}],
        ]
        ret = _determine_step_key(step_metrics_list)
        assert ret is None


class TestGetSubsetName:

    @pytest.mark.parametrize('metric_name,expected', [
        ('train/loss', ('train', 'loss')),
        ('loss_val', ('val', 'loss')),
        ('test-class-acc', ('test', 'class-acc')),
        ('lr', (None, 'lr'))
    ])
    def test(self, metric_name, expected):
        assert _split_subset_name(metric_name) == expected


class TestListStepMetrics:

    def test_default(self):
        step_metrics_list = [
            [{'epoch': 0, 'train_loss': 10, 'val_loss': 10, 'lr': 0.1}],
            [{'epoch': 0, 'train_loss': 10, 'train_cls_loss': 5, 'lr': 0.1}],
        ]
        ret = _list_step_metrics(step_metrics_list)
        expected = [
            'train_loss',
            'val_loss',
            'lr',
            'train_cls_loss'
        ]
        print(ret)
        assert len(ret) == len(expected)
        for e in expected:
            assert e in ret

    def test_compare_subsets(self):
        step_metrics_list = [
            [{'epoch': 0, 'train_loss': 10, 'val_loss': 10, 'lr': 0.1}],
            [{'epoch': 0, 'train_loss': 10, 'train_cls_loss': 5, 'lr': 0.1}],
        ]
        ret = _list_step_metrics(step_metrics_list, compare_subsets=True)
        expected = [
            {'train': 'train_loss', 'val': 'val_loss'},
            {'train': 'train_cls_loss'},
            'lr'
        ]
        assert len(ret) == len(expected)
        for e in expected:
            assert e in ret


class TestVisualizeStepMetrics:

    def test(self):
        opt = {'params': {}, 'metrics': {}}
        run1 = Run(id='1', **opt, step_metrics=[
            {'epoch': 0, 'train_loss': 10, 'val_loss': 5},
            {'epoch': 1, 'train_loss': 5, 'val_loss': 2},
            {'epoch': 2, 'train_loss': 3, 'val_loss': 1},
        ])
        run2 = Run(id='2', **opt, step_metrics=[
            {'epoch': 0, 'train_loss': 10, 'val_loss': 5},
            {'epoch': 1, 'train_loss': 5, 'val_loss': 2},
            {'epoch': 2, 'train_loss': 3, 'val_loss': 1},
        ])
        fig = visualize_step_metrics([run1, run2])
        assert isinstance(fig.image, Image.Image)

    def test_no_step_metrics(self):
        opt = {'params': {}, 'metrics': {}}
        run1 = Run(id='1', **opt, step_metrics=[
            {'epoch': 0, 'train_loss': 10, 'val_loss': 5},
            {'epoch': 1, 'train_loss': 5, 'val_loss': 2},
            {'epoch': 2, 'train_loss': 3, 'val_loss': 1},
        ])
        run2 = Run(id='2', **opt, step_metrics=None)
        fig = visualize_step_metrics([run1, run2])
        assert isinstance(fig.image, Image.Image)
