import torch as t
from .voc_dataset import VOCBboxDataset
from skimage import transform as sktsf
from torchvision import transforms as tvtsf
from . import util
import numpy as np
from utils.config import opt
import cv2
import imgaug as ia
from imgaug import augmenters as iaa
import random
from random import randint

def AddGaussianNoise(im, noise_val):

    img = im.astype(np.float64) / 255.0
    _, row, col = im.shape
    mean = 0
    var = random.uniform(0, noise_val)

    sigma = var ** 0.5
    gaussian = np.random.normal(mean, sigma, (row, col, 1))
    gaussian = np.concatenate((gaussian, gaussian, gaussian), axis=2)
    gaussian = np.reshape(gaussian,(3,row,col))
    gaussian_img = cv2.addWeighted(img, 0.9, gaussian, 0.1, 0) * 255.0

    gaussian_img = np.clip(gaussian_img, 0, 255)
    return gaussian_img.astype(np.uint8)


def ChangeLuminance(im, contrast_range, brightness_range):

        contrast_val = randint(0, contrast_range*2) - contrast_range
        brightness_val = randint(0, brightness_range*2) - brightness_range
        img = np.int16(im)
        img = img * (100+contrast_val)/100  + brightness_val
        img = np.clip(img, 0, 255)
        img = np.uint8(img)
        return img

def blur(im):
    seq = iaa.Sequential([
        iaa.GaussianBlur((0.0, 2.5)),
        iaa.AverageBlur(k=(2, 7)),
    ])
    seq_det = seq.to_deterministic()
    image_aug = seq_det.augment_images([im])[0]

    return image_aug


def inverse_normalize(img):
    if opt.caffe_pretrain:
        img = img + (np.array([122.7717, 115.9465, 102.9801]).reshape(3, 1, 1))
        return img[::-1, :, :]
    # approximate un-normalize for visualize
    return (img * 0.225 + 0.45).clip(min=0, max=1) * 255


def pytorch_normalze(img):
    """
    https://github.com/pytorch/vision/issues/223
    return appr -1~1 RGB
    """
    normalize = tvtsf.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
    img = normalize(t.from_numpy(img))
    return img.numpy()


def caffe_normalize(img):
    """
    return appr -125-125 BGR
    """
    img = img[[2, 1, 0], :, :]  # RGB-BGR
    img = img * 255
    mean = np.array([122.7717, 115.9465, 102.9801]).reshape(3, 1, 1)
    img = (img - mean).astype(np.float32, copy=True)
    return img

###
# @brief size가 다른 이미지에 대해서 resize 및 normalization
# @param img img (~numpy.ndarray): An image. This is in CHW and RGB format.
# @param min_size 이미지 최소 사이즈
# @param max_size 이미지 최대 사이즈
# @return normalize(img) : return A preprocessed image.
###
def preprocess(img, min_size=600, max_size=1000):

    """Preprocess an image for feature extraction.

    The length of the shorter edge is scaled to :obj:`self.min_size`.
    After the scaling, if the length of the longer edge is longer than
    :param min_size:
    :obj:`self.max_size`, the image is scaled to fit the longer edge
    to :obj:`self.max_size`.

    After resizing the image, the image is subtracted by a mean image value
    :obj:`self.mean`.

    Args:
        img (~numpy.ndarray): An image. This is in CHW and RGB format.
            The range of its value is :math:`[0, 255]`.
         (~numpy.ndarray): An image. This is in CHW and RGB format.
            The range of its value is :math:`[0, 255]`.

    Returns:
        ~numpy.ndarray:
        A preprocessed image.

    """
    C, H, W = img.shape
    scale1 = min_size / min(H, W)
    scale2 = max_size / max(H, W)
    scale = min(scale1, scale2)
    img = img / 255.
    img = sktsf.resize(img, (C, H * scale, W * scale), mode='reflect')
    # both the longer and shorter should be less than
    # max_size and min_size
    if opt.caffe_pretrain:
        normalize = caffe_normalize
    else:
        normalize = pytorch_normalze
    return normalize(img)

###
# @brief 이미지 크기 변경 및 B.B 크기 변경
###
class Transform(object):
    # 줄어든 비율 만큼 B.B의 크기도 바꿔준다.
    def __init__(self, min_size=600, max_size=1000):
        self.min_size = min_size
        self.max_size = max_size

    def __call__(self, in_data):
        img, bbox, label = in_data
        _, H, W = img.shape
        # 이미지 resize
        img = preprocess(img, self.min_size, self.max_size)
        _, o_H, o_W = img.shape
        scale = o_H / H
        bbox = util.resize_bbox(bbox, (H, W), (o_H, o_W))

        # horizontally flip
        img, params = util.random_flip(
            img, x_random=True, return_param=True)
        bbox = util.flip_bbox(
            bbox, (o_H, o_W), x_flip=params['x_flip'])

        return img, bbox, label, scale


class Dataset:
    def __init__(self, opt):
        self.opt = opt
        self.db = VOCBboxDataset(opt.voc_data_dir)
        self.tsf = Transform(opt.min_size, opt.max_size)

    def __getitem__(self, idx):
        # voc_dataset.py --> get_example
        ori_img, bbox, label, difficult = self.db.get_example(idx)
        # data augmentation
        ori_img = AddGaussianNoise(ori_img, 0.05)
        ori_img = ChangeLuminance(ori_img,10,20)

        img, bbox, label, scale = self.tsf((ori_img, bbox, label))
        # TODO: check whose stride is negative to fix this instead copy all
        # some of the strides of a given numpy array are negative.
        return img.copy(), bbox.copy(), label.copy(), scale

    def __len__(self):
        return len(self.db)


class TestDataset:
    def __init__(self, opt, split='test', use_difficult=True):
        self.opt = opt
        self.db = VOCBboxDataset(opt.voc_data_dir, split=split, use_difficult=use_difficult)

    def __getitem__(self, idx):
        ori_img, bbox, label, difficult = self.db.get_example(idx)
        img = preprocess(ori_img)
        return img, ori_img.shape[1:], bbox, label, difficult

    def __len__(self):
        return len(self.db)
