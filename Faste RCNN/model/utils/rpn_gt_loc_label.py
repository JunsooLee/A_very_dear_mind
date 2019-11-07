import numpy as np

from model.utils.bbox_tools import bbox2loc, bbox_iou

class AnchorTargetCreator(object):
    """Assign the ground truth bounding boxes to anchors.

    Assigns the ground truth bounding boxes to anchors for training Region
    Proposal Networks introduced in Faster R-CNN [#]_.

    Offsets and scales to match anchors to the ground truth are
    calculated using the encoding scheme of
    :func:`model.utils.bbox_tools.bbox2loc`.

    .. [#] Shaoqing Ren, Kaiming He, Ross Girshick, Jian Sun. \
    Faster R-CNN: Towards Real-Time Object Detection with \
    Region Proposal Networks. NIPS 2015.


     @param    n_sample (int): The number of regions to produce.

     @param    pos_iou_thresh (float): Anchors with IoU above this threshold will be assigned as positive.

     @param    neg_iou_thresh (float): Anchors with IoU below this threshold will be assigned as negative.

     @param    pos_ratio (float): Ratio of positive regions in the sampled regions.

    """

    def __init__(self,
                 n_sample=256,
                 pos_iou_thresh=0.7, neg_iou_thresh=0.3,
                 pos_ratio=0.5):
        self.n_sample = n_sample
        self.pos_iou_thresh = pos_iou_thresh
        self.neg_iou_thresh = neg_iou_thresh
        self.pos_ratio = pos_ratio

    ###
    # @brief RPN을 통해서 예측한
    # @param bbox B.B GT
    # @param anchor F.M 한 픽셀당 9개의 anchor 좌표 초기값, shape = (F.M H * W * A, 4)
    # @param img_size 이미지 크기
    # @return loc : 전체 anchor 좌표와 B.B와의 상대좌표를 기록한 배열 --> shape = (F.M H * W * A, 4) 이지만 안에는 값은 inside_index 안에만 기록되어 있음
    # @return label : anchor에 대한 label을 기록한 배열 --> shape = (F.M H * W * A, 4)
    ###
    def __call__(self, bbox, anchor, img_size):
        """Assign ground truth supervision to sampled subset of anchors.

        Types of input arrays and output arrays are same.

        Here are notations.

        * :math:`S` is the number of anchors.
        * :math:`R` is the number of bounding boxes.

        Args:
            bbox (array): Coordinates of bounding boxes. Its shape is
                :math:`(R, 4)`.
            anchor (array): Coordinates of anchors. Its shape is
                :math:`(S, 4)`.
            img_size (tuple of ints): A tuple :obj:`H, W`, which
                is a tuple of height and width of an image.

        Returns:
            (array, array):

            #NOTE: it's scale not only  offset
            * **loc**: Offsets and scales to match the anchors to \
                the ground truth bounding boxes. Its shape is :math:`(S, 4)`.
            * **label**: Labels of anchors with values \
                :obj:`(1=positive, 0=negative, -1=ignore)`. Its shape \
                is :math:`(S,)`.

        """

        img_H, img_W = img_size

        # 전체 base anchor 사이즈
        n_anchor = len(anchor)
        inside_index = _get_inside_index(anchor, img_H, img_W)
        anchor = anchor[inside_index]
        argmax_ious, label = self._create_label(
            inside_index, anchor, bbox)
        # compute bounding box regression targets
        # anchor 와 실제 B.B 의 위치와의 차이를 나타낸다. Y,X, height, width 로 구성되있음
        loc = bbox2loc(anchor, bbox[argmax_ious])

        # map up to original set of anchors
        # labeling을 한 index의 label값만 가져온다.
        label = _unmap(label, n_anchor, inside_index, fill=-1)
        # 위에서 선택된 anchor들에서 실제 B.B.와의 상대적인 거리를 loc에 저장. 배열은 전체 base anchor size 만큼 설정, inside_index 만 값을 가진다.
        loc = _unmap(loc, n_anchor, inside_index, fill=0)
        return loc, label

    ###
    # @brief - 1. 각 anchor마다 최대 iou가 0.3 미만이면 해당 anchor의 label은 0이다.
    # @brief - 2.  각 anchor마다 최대 iou가 0.7 이상이면 해당 anchor의 label은 1이다.
    # @brief - 3. 각 gt box마다 최대 iou를 가지는 anchor의 label은 1이다.
    # @brief - (anchor label = 0: background, 1: object, -1: 애매하므로 무시)
    # @param inside_index 이미지 size 안에 존재하는 anchor index
    # @param anchor anchor box
    # @param bbox B.B GT
    # @return argmax_ious anchor 박스에 대한 IoU
    # @return label argmax_ious에 대한 labeling 값
    ###
    def _create_label(self, inside_index, anchor, bbox):
        # label: 1 is positive, 0 is negative, -1 is dont care
        label = np.empty((len(inside_index),), dtype=np.int32)
        label.fill(-1)

        argmax_ious, max_ious, gt_argmax_ious = \
            self._calc_ious(anchor, bbox, inside_index)

        # assign negative labels first so that positive labels can clobber them
        label[max_ious < self.neg_iou_thresh] = 0

        # positive label: for each gt, anchor with highest iou
        label[gt_argmax_ious] = 1

        # positive label: above threshold IOU
        label[max_ious >= self.pos_iou_thresh] = 1

        # subsample positive labels if we have too many
        n_pos = int(self.pos_ratio * self.n_sample)
        pos_index = np.where(label == 1)[0]
        if len(pos_index) > n_pos:
            disable_index = np.random.choice(
                pos_index, size=(len(pos_index) - n_pos), replace=False)
            label[disable_index] = -1

        # subsample negative labels if we have too many
        n_neg = self.n_sample - np.sum(label == 1)
        neg_index = np.where(label == 0)[0]
        if len(neg_index) > n_neg:
            disable_index = np.random.choice(
                neg_index, size=(len(neg_index) - n_neg), replace=False)
            label[disable_index] = -1

        return argmax_ious, label

    # @brief GT와 anchor 와의 iou 구하는 함수
    def _calc_ious(self, anchor, bbox, inside_index):
        # ious between the anchors and the gt boxes
        ious = bbox_iou(anchor, bbox)
        argmax_ious = ious.argmax(axis=1)
        max_ious = ious[np.arange(len(inside_index)), argmax_ious]
        gt_argmax_ious = ious.argmax(axis=0)
        gt_max_ious = ious[gt_argmax_ious, np.arange(ious.shape[1])]
        gt_argmax_ious = np.where(ious == gt_max_ious)[0]

        return argmax_ious, max_ious, gt_argmax_ious


def _unmap(data, count, index, fill=0):
    # Unmap a subset of item (data) back to the original set of items (of size count)

    if len(data.shape) == 1:
        ret = np.empty((count,), dtype=data.dtype)
        ret.fill(fill)
        ret[index] = data
    else:
        ret = np.empty((count,) + data.shape[1:], dtype=data.dtype)
        ret.fill(fill)
        ret[index, :] = data
    return ret


###
# @brief 이미지 안에있는 anchor 박스의 index 반환
# @param anchor F.M 한 픽셀당 9개의 anchor 좌표 초기값, shape = (H * W * A, 4)
# @param H image height
# @param W image width
# @return index_inside : 이미지 size 안에 있는 anchor의 index
###

def _get_inside_index(anchor, H, W):
    # Calc indicies of anchors which are located completely inside of the image
    # whose size is speficied.
    index_inside = np.where(
        (anchor[:, 0] >= 0) &
        (anchor[:, 1] >= 0) &
        (anchor[:, 2] <= H) &
        (anchor[:, 3] <= W)
    )[0]
    return index_inside