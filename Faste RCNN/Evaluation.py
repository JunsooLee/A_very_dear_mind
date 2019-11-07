import matplotlib.pyplot as plt
from utils.config import opt
from utils.data_load import save_pkl, load_pkl
import numpy as np
from torch import nn
from torch.utils import data as data_
from tqdm import tqdm
import torch as t
from utils import array_tool as at
from torch.autograd import Variable

# Load Data
from data.dataset import Dataset, TestDataset, inverse_normalize
# Load Net and Trainer
from model.faster_rcnn import FasterRCNN
from trainer.trainer import FasterRCNNTrainer

from utils.eval_tool import eval_detection_voc

def eval(dataloader, faster_rcnn, test_num=10000):
    pred_bboxes, pred_labels, pred_scores = list(), list(), list()
    gt_bboxes, gt_labels, gt_difficults = list(), list(), list()
    for ii, (imgs, sizes, gt_bboxes_, gt_labels_, gt_difficults_) in tqdm(enumerate(dataloader)):
        sizes = [sizes[0][0], sizes[1][0]]
        pred_bboxes_, pred_labels_, pred_scores_ = faster_rcnn.predict(imgs, [sizes])
        gt_bboxes += list(gt_bboxes_.numpy())
        gt_labels += list(gt_labels_.numpy())
        gt_difficults += list(gt_difficults_.numpy())
        pred_bboxes += pred_bboxes_
        pred_labels += pred_labels_
        pred_scores += pred_scores_
        if ii == test_num: break

    result = eval_detection_voc(
        pred_bboxes, pred_labels, pred_scores,
        gt_bboxes, gt_labels, gt_difficults,
        use_07_metric=True)
    return result

if __name__ == '__main__':
    faster_rcnn = FasterRCNN()

    testset = TestDataset(opt)
    test_dataloader = data_.DataLoader(testset,
                                       batch_size=1,
                                       num_workers=8,
                                       shuffle=False,
                                       pin_memory=True)

    eval_result = eval(test_dataloader, faster_rcnn, test_num=1000)
    print(eval_result)