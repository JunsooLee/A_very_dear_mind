import numpy as np
from utils.anchors import generate_anchor_base, get_anchors, get_rois_from_loc_anchors
from utils.py_nms import py_cpu_nms
from torch import nn
from torch.nn import functional as F
import torch

class RegionProposalNetwork(nn.Module):
    """
    @brief Region Proposal Network introduced in Faster R-CNN.

    @param  in_channels (int): The channel size of input.

    @param  mid_channels (int): The channel size of the intermediate tensor.

    @param  ratios (list of floats): This is ratios of width to height of the anchors.

    @param  anchor_scales (list of numbers): This is areas of anchors.
           Those areas will be the product of the square of an element in
           :obj:`anchor_scales` and the original area of the reference window.

    @param  feat_stride (int): Stride size after extracting features from an image.

    @param  initialW (callable): Initial weight value. If :obj:`None` then this
            function uses Gaussian distribution scaled by 0.1 to initialize weight.
            May also be a callable that takes an array and edits its values.

    @param proposal_creator_params (dict): Key valued paramters for
           :class:`model.utils.creator_tools.ProposalCreator`.

    .. seealso::
        :class:`~model.utils.creator_tools.ProposalCreator`

    """

    def __init__(
            self, in_channels=512, mid_channels=512, ratios=[0.5, 1, 2],
            scales=[0.5, 1, 2], feat_stride=16):
        super(RegionProposalNetwork, self).__init__()
        # prepare anchor base
        # side_length 는 16 * 16 의 single box (block side length)
        self.anchor_base = generate_anchor_base(side_length=16, 
            ratios=ratios, scales=scales, strides=feat_stride)
        self.feat_stride = feat_stride
        # network params
        n_anchor = self.anchor_base.shape[0] # n_anchor = 9 : anchor의
        self.conv1 = nn.Conv2d(in_channels, mid_channels, 3, 1, 1) # input, output, kernel, stride, padding : 3 * 3 filter 해준다.
        self.score = nn.Conv2d(mid_channels, n_anchor * 2, 1, 1, 0) # B.B 에 대한 점수 object 인지 object 가 아닌지
        self.loc = nn.Conv2d(mid_channels, n_anchor * 4, 1, 1, 0) # regression 에 대한 위치 (regression location)
        normal_init(self.conv1, 0, 0.01)
        normal_init(self.score, 0, 0.01)
        normal_init(self.loc, 0, 0.01)



    ###
    # @brief Forward Region Proposal Network.
    # @param h F.M 의미, shape = (N, C, H, W)
    # @param img_size Resize 된 크기의 input image
    # @param scale Resize의 비율
    # @return rpn_locs : F.M의 한 픽셀에 해당하는 9개의 anchor 좌표, shape = (N, H W A, 4)
    # @return rpn_scores : F.M의 한 픽셀에 해당하는 9개의 anchor 각각에 대한 object 존재 확률값 shape = (N, H W A, 2)
    # @return rois : 예측된 sample anchor
    # @return [0]*len(rois) : sample anchor 개수 만큼의 list
    # @return anchors : F.M 한 픽셀당 9개의 anchor 좌표 초기값, shape = (H W A, 4)
    ###
    def forward(self, h, img_size, scale=1.):
        """
        - :math:`N` is batch size.
        - :math:`C` channel size of the input.
        - :math:`H` and :math:`W` are height and witdh of the input feature.
        - :math:`A` is number of anchors assigned to each pixel.

        Args:
            x (~torch.autograd.Variable): The Features extracted from images.
                Its shape is :math:`(N, C, H, W)`.

            img_size (tuple of ints): A tuple :obj:`height, width`, which contains image size after scaling.

            scale (float): The amount of scaling done to the input images after reading them from files.

        Returns:
            (~torch.autograd.Variable, ~torch.autograd.Variable, array, array, array):

            This is a tuple of five following values.

            * **rpn_locs**: Predicted bounding box offsets and scales for \
                anchors. Its shape is :math:`(N, H W A, 4)`.
            * **rpn_scores**:  Predicted foreground scores for \
                anchors. Its shape is :math:`(N, H W A, 2)`.
            * **rois**: A bounding box array containing coordinates of \
                proposal boxes.  This is a concatenation of bounding box \
                arrays from multiple images in the batch. \
                Its shape is :math:`(R', 4)`. Given :math:`R_i` predicted \
                bounding boxes from the :math:`i` th image, \
                :math:`R' = \\sum _{i=1} ^ N R_i`.
            * **roi_indices**: An array containing indices of images to
                which RoIs correspond to. Its shape is :math:`(R',)`.
            * **anchor**: Coordinates of enumerated shifted anchors. \
                Its shape is :math:`(H W A, 4)`.

        """
        # NMS에 넣기 전 뽑는 objectness가 높은 순서의 anchor 개수
        n_pre_nms = 12000
        # NMS로 뽑을 anchor 수 (최대 2000개, 2000개보다 적을 수 있음)
        n_post_nms = 2000
        # NMS G.T 와 겹치는 anchor의 IoU threshold
        nms_thresh = 0.7

        # feature map의 shape
        n, _, hh, ww = h.shape

        # utils --> anchors.py
        anchors = get_anchors(self.anchor_base, self.feat_stride, hh, ww)


        hidd = F.relu(self.conv1(h))
        # rpn_locs shape = 1 * 36(9 * 4) * feature map height * feature map width
        rpn_locs = self.loc(hidd)
        # rpn_scores shape = 1 * 18(9 * 2) * feature map height * feature map width
        rpn_scores = self.score(hidd)

        # shape : 1 * (feature height * feature width * 9) * 4
        rpn_locs = rpn_locs.permute(0, 2, 3, 1).contiguous().view(n, -1, 4)
        # shape : 1 * (feature height * feature width * 9) * 2
        rpn_scores = rpn_scores.permute(0, 2, 3, 1).contiguous().view(n, -1, 2)
        # 0 or 1 중 1(object에 대한 확률 값)
        scores = rpn_scores[:,:,1].data.cpu().numpy()[0]
        
        # RPN을 통해서 나온 anchor값(상대좌표)을 input image 크기의 anchor 좌표로 변환
        rois = get_rois_from_loc_anchors(anchors, rpn_locs[0].data.cpu().numpy())

        # rois의 좌표 값이 이미지 크기 밖에 있을 경우 np,clip을 통해 보정
        rois[:, ::2] = np.clip(rois[:, ::2], 0, img_size[0])
        rois[:, 1::2] = np.clip(rois[:, 1::2], 0, img_size[1])

        # scale: change type (tensor -> array)
        scale = scale.numpy()

        # 이미지를 resize 하기 때문에 최소 픽셀값 "16" 값에도 scale 곱함
        min_size = 16.
        min_size = min_size * scale

        hs = rois[:, 2] - rois[:, 0] # height
        ws = rois[:, 3] - rois[:, 1] # width

        keep = np.where((hs >= min_size) & (ws >= min_size))[0]
        rois = rois[keep, :] # 최소 픽셀 이상인 anchor의 select (anchor 박스의 크기가 16 * 16 보다 작으면 탈락)
        scores = scores[keep]

        # ravel(): 다차원 배열을 1차원으로 펼침
        # argsort(): 오름차순 정렬된 원소의 index를 반환
        # [::-1]: 역순으로 반환
        # order: object 존재 score가 높은 순서대로 index 저장
        order = scores.ravel().argsort()[::-1]
        if n_pre_nms > 0:
            order = order[:n_pre_nms] # score 가 높은 순서대로 12000개 뽑음
        rois = rois[order, :]

        # NMS (py_nms.py)
        keep = py_cpu_nms(rois, nms_thresh)
        # IoU 0.7보다 큰 것중에서 상위 2000개를 선택. 꼭 2000개가 아니라 2000개보다 작을 수도 있다
        keep = keep[:n_post_nms]
        # 2000개 정도를 (2000보다 작은수도 있음) 뽑은 것의 roi만 저장
        rois = rois[keep]
        return rpn_locs, rpn_scores, rois, [0]*len(rois), anchors

###
# @brief weight initalizer: truncated normal and random normal.
###
def normal_init(m, mean, stddev, truncated=False):
    # x is a parameter
    if truncated:
        m.weight.data.normal_().fmod_(2).mul_(stddev).add_(mean)  # not a perfect approximation
    else:
        m.weight.data.normal_(mean, stddev)
        m.bias.data.zero_()