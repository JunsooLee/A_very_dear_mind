###
# @mainpage Faster_RCNN (base network: VGG16)
# @section CREATEINFO 작성정보
# - 작성자 : 황병훈
# - 작성일: 2019 - 11 - 05
# @brief 세탁 테그 인식을 위한 Faster RCNN fine tuning code
###

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
import torch


from data.dataset import Dataset, TestDataset, inverse_normalize
from model.faster_rcnn import FasterRCNN
from trainer.trainer import FasterRCNNTrainer
from utils.eval_tool import eval_detection_voc

###
# @fn def eval(dataloader, faster_rcnn, test_num=200)
# @brief "MAP"를 구하기 위한 함수
# @param dataloader 평가할 이미지에 대한 option
# @param faster_rcnn 학습된 model
# @param test_num 평가할 image 개수
# @return result 'ap' 와 'map' 으로 구성
###
def eval(dataloader, faster_rcnn, test_num=1000):
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

###
# @brief Main Train 함수
###
if __name__ == '__main__':
    dataset = Dataset(opt)
    dataloader = data_.DataLoader(dataset,
                                  batch_size=1,
                                  shuffle=True,
                                  num_workers=opt.num_workers)

    testset = TestDataset(opt)
    test_dataloader = data_.DataLoader(testset,
                                       batch_size=1,
                                       num_workers=opt.test_num_workers,
                                       shuffle=False, \
                                       pin_memory=True
                                       )

    # faster_rcnn.py --> roi head & rpn 초기화
    faster_rcnn = FasterRCNN()
    trainer = FasterRCNNTrainer(faster_rcnn).cuda()

    # pre train model 경로 설정
    if opt.load_path:
        trainer.load(opt.load_path)
        print('load pretrained model from %s' % opt.load_path)

    lr_ = opt.lr
    best_map = 0
    for epoch in range(20):
        loss_list_roi_cls = []
        loss_list_roi_loc = []
        loss_list_rpn_cls = []
        loss_list_rpn_loc = []
        for ii, (img, bbox_, label_, scale) in tqdm(enumerate(dataloader)):
            # scale: 이미지 resize 비율 의미
            scale = at.scalar(scale)
            img, bbox, label = img.cuda().float(), bbox_.cuda(), label_.cuda()
            img, bbox, label = Variable(img), Variable(bbox), Variable(label)
            # network forwarding
            loss_list = trainer.train_step(img, bbox, label, scale)
            loss_list_roi_cls.append(loss_list.roi_cls_loss)
            loss_list_roi_loc.append(loss_list.roi_loc_loss)
            loss_list_rpn_cls.append(loss_list.rpn_cls_loss)
            loss_list_rpn_loc.append(loss_list.rpn_loc_loss)

        print("--------------------------")
        print("current epoch: ", epoch)
        print("rpn_loc loss: ", torch.mean(torch.stack(loss_list_rpn_loc)))
        print("rpn_cls loss: ", torch.mean(torch.stack(loss_list_rpn_cls)))
        print("roi_loc loss: ", torch.mean(torch.stack(loss_list_roi_loc)))
        print("roi_cls loss: ", torch.mean(torch.stack(loss_list_roi_cls)))
        print("--------------------------")
        # 학습된 모델 저장
        trainer.save(save_optimizer=True, best_map=epoch)

        # Learning rate 0.1 줄이기
        if epoch == 10:
            trainer.faster_rcnn.scale_lr(opt.lr_decay)
            lr_ = lr_ * opt.lr_decay


    eval_result = eval(test_dataloader, faster_rcnn, test_num=opt.test_num)

    if eval_result['map'] > best_map:
        best_map = eval_result['map']
        # 학습된 모델 저장
        best_path = trainer.save(best_map=best_map)