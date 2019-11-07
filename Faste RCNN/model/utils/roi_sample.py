from model.utils.bbox_tools import bbox2loc, bbox_iou
import numpy as np

class ProposalTargetCreator(object):
    """Assign ground truth bounding boxes to given RoIs.

    The :meth:`__call__` of this class generates training targets
    for each object proposal.
    This is used to train Faster RCNN [#]_.

    .. [#] Shaoqing Ren, Kaiming He, Ross Girshick, Jian Sun. \
    Faster R-CNN: Towards Real-Time Object Detection with \
    Region Proposal Networks. NIPS 2015.

    Args:
        n_sample (int): The number of sampled regions.
        pos_ratio (float): Fraction of regions that is labeled as a
            foreground. # sample에서 pos한 비율
        pos_iou_thresh (float): IoU threshold for a RoI to be considered as a
            foreground. #pos로 간주되기 위한 GT와 겹치는 iou
        neg_iou_thresh_hi (float): RoI is considered to be the background
            if IoU is in # neg로 간주되기 위한 back ground와 겹치는 비율
            [:obj:`neg_iou_thresh_hi`, :obj:`neg_iou_thresh_hi`).
        neg_iou_thresh_lo (float): See above.

    """
    # TODO: ratio and thresh 부분 조절에 따른 map 확인해 보기
    def __init__(self,
                 n_sample=128,
                 pos_ratio=0.25, pos_iou_thresh=0.5,
                 neg_iou_thresh_hi=0.5, neg_iou_thresh_lo=0.0
                 ):
        self.n_sample = n_sample
        self.pos_ratio = pos_ratio
        self.pos_iou_thresh = pos_iou_thresh
        self.neg_iou_thresh_hi = neg_iou_thresh_hi
        self.neg_iou_thresh_lo = neg_iou_thresh_lo

    ###
    # @brief RPN 네트워크에서 뽑은 sample anchor 중에서 IoU를 기준으로 pos와 negative의 비율을 1:3으로 맞춰
    # @brief 실제 object 가 있을법한 roi와 background 만 있는 roi를 뽑는다.
    # @param roi 예측된 sample anchor (최대 2000개)
    # @param bbox B.B 정보
    # @param label B.B label 정보
    # @param loc_normalize_mean (0., 0., 0., 0.)
    # @param loc_normalize_std (0.1, 0.1, 0.2, 0.2)
    # @return sample_roi : sample anchor 중에서 pos 와 neg 비율 대로 뽑은 것
    # @return gt_roi_loc : 위에서 뽑은 anchor 와 B.B G.T와의 상대좌표
    # @return gt_roi_label : 위에서 뽑은 anchor 의 label
    ###
    def __call__(self, roi, bbox, label,
                 loc_normalize_mean=(0., 0., 0., 0.),
                 loc_normalize_std=(0.1, 0.1, 0.2, 0.2)):
        """Assigns ground truth to sampled proposals.

        This function samples total of :obj:`self.n_sample` RoIs
        from the combination of :obj:`roi` and :obj:`bbox`.
        The RoIs are assigned with the ground truth class labels as well as
        bounding box offsets and scales to match the ground truth bounding
        boxes. As many as :obj:`pos_ratio * self.n_sample` RoIs are
        sampled as foregrounds.

        Offsets and scales of bounding boxes are calculated using
        :func:`model.utils.bbox_tools.bbox2loc`.
        Also, types of input arrays and output arrays are same.

        Here are notations.

        * :math:`S` is the total number of sampled RoIs, which equals \
            :obj:`self.n_sample`.
        * :math:`L` is number of object classes possibly including the \
            background.

        Args:
            roi (array): Region of Interests (RoIs) from which we sample.
                Its shape is :math:`(R, 4)`
            bbox (array): The coordinates of ground truth bounding boxes.
                Its shape is :math:`(R', 4)`.
            label (array): Ground truth bounding box labels. Its shape
                is :math:`(R',)`. Its range is :math:`[0, L - 1]`, where
                :math:`L` is the number of foreground classes.
            loc_normalize_mean (tuple of four floats): Mean values to normalize
                coordinates of bouding boxes.
            loc_normalize_std (tupler of four floats): Standard deviation of
                the coordinates of bounding boxes.

        Returns:
            (array, array, array):

            * **sample_roi**: Regions of interests that are sampled. \
                Its shape is :math:`(S, 4)`.
            * **gt_roi_loc**: Offsets and scales to match \
                the sampled RoIs to the ground truth bounding boxes. \
                Its shape is :math:`(S, 4)`.
            * **gt_roi_label**: Labels assigned to sampled RoIs. Its shape is \
                :math:`(S,)`. Its range is :math:`[0, L]`. The label with \
                value 0 is the background.

        """
        n_bbox, _ = bbox.shape
        # sample로 뽑은 roi뒤에 B.B 정보를 붙인다.
        roi = np.concatenate((roi, bbox), axis=0)


        pos_roi_per_image = np.round(self.n_sample * self.pos_ratio) # 뽑을 pos 개수 128 * 0.25 = 32

        iou = bbox_iou(roi, bbox) # sample anchor에 대한 iou
        gt_assignment = iou.argmax(axis=1) # B.B 카테고리 중에서 iou가 큰 index값 설정
        max_iou = iou.max(axis=1) # B.B 카테고리 중에서 iou가 큰 값 설정

        # Offset range of classes from [0, n_fg_class - 1] to [1, n_fg_class].
        # +1 의미: 해주는 이유는 background 가 0으로 붙기 때문이다.
        gt_roi_label = label[gt_assignment] + 1

        # Select foreground RoIs as those with : roi 중에서 object 인 것만 select
        pos_index = np.where(max_iou >= self.pos_iou_thresh)[0] # 0.5 보다 큰 것만 select
        pos_roi_per_this_image = int(min(pos_roi_per_image, pos_index.size))
        if pos_index.size > 0:
            pos_index = np.random.choice(
                pos_index, size=pos_roi_per_this_image, replace=False)

        # Select background RoIs as those within : roi 중에서 background 인 것만 select
        neg_index = np.where((max_iou < self.neg_iou_thresh_hi) &
                             (max_iou >= self.neg_iou_thresh_lo))[0]
        neg_roi_per_this_image = self.n_sample - pos_roi_per_this_image
        neg_roi_per_this_image = int(min(neg_roi_per_this_image,
                                         neg_index.size))
        if neg_index.size > 0:
            neg_index = np.random.choice(
                neg_index, size=neg_roi_per_this_image, replace=False)

        # The indices that we're selecting (both positive and negative).
        keep_index = np.append(pos_index, neg_index) # pos roi index 뒤에 neg roi index를 붙인다.
        gt_roi_label = gt_roi_label[keep_index]
        # sample roi 의 negative 즉 background label 0으로 할당.
        gt_roi_label[pos_roi_per_this_image:] = 0
        sample_roi = roi[keep_index]

        # Compute offsets and scales to match sampled RoIs to the GTs.
        # @note 뽑힌 sample roi(pos & negative 비율 1 : 3) 와 실제 B.B 와의 상대좌표
        gt_roi_loc = bbox2loc(sample_roi, bbox[gt_assignment[keep_index]])
        gt_roi_loc = ((gt_roi_loc - np.array(loc_normalize_mean, np.float32)
                       ) / np.array(loc_normalize_std, np.float32))

        return sample_roi, gt_roi_loc, gt_roi_label
