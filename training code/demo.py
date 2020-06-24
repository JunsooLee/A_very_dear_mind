import os
import torch as t
from utils.config import opt
from model.faster_rcnn import FasterRCNN
from trainer.trainer import FasterRCNNTrainer
from data.util import read_image
from utils.vis_tool import vis_bbox
from utils import array_tool as at
import numpy as np
import matplotlib.pyplot as plt
from data.dataset import Dataset, TestDataset, inverse_normalize
import xml.etree.ElementTree as ET
import warnings
warnings.simplefilter("ignore", UserWarning)

VOC_BBOX_LABEL_NAMES = (
    'do_not_wash',
    'do_not_bleach',
    'do_not_iron',
    'do_not_dry_clean'
    )

# img = read_image('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/data/VOCdevkit/VOC2007/dataset_laundry tag/000294.jpg')
# img = read_image('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/data\VOCdevkit/VOC2007/dataset_laundry tag/000015.jpg')
# img = read_image('C:/Users/user/Desktop/최종/001780.jpg')
img = read_image('./test_image/test2.jpg')
# img = read_image('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/input/images-optional/000813.jpg')


img = t.from_numpy(img)[None]



faster_rcnn = FasterRCNN()
trainer = FasterRCNNTrainer(faster_rcnn).cuda()


# trainer.load('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/checkpoints/fasterrcnn_11072246_7.pth')
trainer.load('./checkpoints/fasterrcnn_11080821_94%.pth')
# trainer.load('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/checkpoints/fasterrcnn_11070910_0.21.pth')


opt.caffe_pretrain=False
ori_img_ = inverse_normalize(at.tonumpy(img[0]))

_bboxes, _labels, _scores = trainer.faster_rcnn.predict(img,visualize=True)

output_img = vis_bbox(at.tonumpy(img[0]),
                      at.tonumpy(_bboxes[0]),
                      at.tonumpy(_labels[0]).reshape(-1),
                      at.tonumpy(_scores[0]).reshape(-1))
plt.show()
