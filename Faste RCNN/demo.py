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

VOC_BBOX_LABEL_NAMES = (
    'do_not_wash',
    'do_not_bleach',
    'do_not_iron',
    'do_not_dry_clean'
    )

# img = read_image('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/data/VOCdevkit/VOC2007/dataset_laundry tag/000294.jpg')
# img = read_image('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/data\VOCdevkit/VOC2007/dataset_laundry tag/000015.jpg')
# img = read_image('C:/Users/user/Desktop/최종/001780.jpg')
img = read_image('C:/Users/user/Desktop/1.jpg')

img = t.from_numpy(img)[None]

anno = ET.parse(
    # os.path.join(self.data_dir, 'Annotations', id_ + '.xml'))
    os.path.join('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/data\VOCdevkit/VOC2007/dataset_laundry tag_xml/000015.xml'))
bbox = list()
label = list()
difficult = list()
for obj in anno.findall('object'):
    # when in not using difficult split, and the object is
    # difficult, skipt it.

    difficult.append(int(obj.find('difficult').text))
    bndbox_anno = obj.find('bndbox')
    # subtract 1 to make pixel indexes 0-based
    bbox.append([
        int(bndbox_anno.find(tag).text) - 1
        for tag in ('ymin', 'xmin', 'ymax', 'xmax')])
    name = obj.find('name').text.lower().strip()
    # print(name)
    label.append(VOC_BBOX_LABEL_NAMES.index(name))
print(bbox)
bbox = np.stack(bbox).astype(np.float32)
label = np.stack(label).astype(np.int32)

faster_rcnn = FasterRCNN()
trainer = FasterRCNNTrainer(faster_rcnn).cuda()

trainer.load('C:/Users/user/PycharmProjects/Faster-RCNN-Pytorch_6/checkpoints/fasterrcnn_11070910_0.21.pth')
opt.caffe_pretrain=False # this model was trained from torchvision-pretrained model
ori_img_ = inverse_normalize(at.tonumpy(img[0]))
# gt_img = vis_bbox(img,
#                   at.tonumpy(bbox_[0]),
#                   at.tonumpy(label_[0]))
# trainer.vis.img('gt_img', gt_img)

_bboxes, _labels, _scores = trainer.faster_rcnn.predict(img,visualize=True)
output_img = vis_bbox(at.tonumpy(img[0]),
                      at.tonumpy(_bboxes[0]),
                      at.tonumpy(_labels[0]).reshape(-1),
                      at.tonumpy(_scores[0]).reshape(-1))
plt.show()
print("done")
# it failed to find the dog, but if you set threshold from 0.7 to 0.6, you'll find it