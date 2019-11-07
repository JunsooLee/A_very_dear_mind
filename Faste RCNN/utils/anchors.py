import numpy as np

###
# @brief (input image size / 16) * (input image size / 16) * 9 개의 기본 anchor 생성
# @brief base anchor of the original image
###
def generate_anchor_base(side_length=16, ratios=[0.5, 1, 2],
                         scales=[0.5, 1, 2], strides=16):
    """
    Generate anchors for a single 16*16 block. Then transform the anchors to the original image space.
    """
    py = side_length / 2.
    px = side_length / 2.
    # anchor_base shape: <class 'tuple'> (9,4)
    anchor_base = np.zeros((len(ratios) * len(scales), 4),
                           dtype=np.float32)

    for i in range(len(ratios)):
        for j in range(len(scales)):
            h = side_length * strides * scales[j] * np.sqrt(ratios[i])
            w = side_length * strides * scales[j] * np.sqrt(1. / ratios[i])

            index = i * len(scales) + j
            anchor_base[index, 0] = py - h / 2.
            anchor_base[index, 1] = px - w / 2.
            anchor_base[index, 2] = py + h / 2.
            anchor_base[index, 3] = px + w / 2.
    return anchor_base

###
# @brief F.M 한 픽셀에 대응하는 3개의 크기 * 3개의 비율을 가지는 9개의 기본 anchor 생성
# @param anchor_base
# @param feat_stride 16(input image 에서 16개 픽셀에 대응)
# @param height F.M height
# @param width F.M width
# @return anchors : F.M 모든 픽셀에 대한 초기 anchor 위치, shape = (F.M height * width * 9 * 4)
###
def get_anchors(anchor_base, feat_stride, height, width):

    # if height = 512 * width = 512 일 경우
    # anchors_y = 0, 16 ,32 ...
    anchors_y = np.arange(height) * feat_stride
    anchors_x = np.arange(width) * feat_stride

    # meshgrid는 사각형의 조합을 의미
    # anchor_x = shape 512 * 512 / value 0, 16, 32 ...
    # anchor_y = shape 512 * 512 / value 0, 0, 0 / 1, 1, 1 / 2, 2, 2
    anchors_x, anchors_y = np.meshgrid(anchors_x, anchors_y)

    # shift shape: (feature map height * feature map width) * 4(좌표)
    shift = np.stack((anchors_y.ravel(), anchors_x.ravel(),
                      anchors_y.ravel(), anchors_x.ravel()), axis=1)
    anchors = np.repeat(shift, repeats=len(anchor_base), axis=0) + \
        np.tile(anchor_base, [len(shift),1])
    return anchors

###
# @brief RPN 네트워크를 통해 나온 anchor 좌표(상대좌표)값을 input image에 매칭
# @param anchors F.M 한 픽셀의 9개의 anchor 좌표 (`p_{ymin}, p_{xmin}, p_{ymax}, p_{xmax}`)
# @param rpn_locs RPN을 통해서 예측한 anchor 좌표, (feature height * feature width * 9 * 4[t_y, t_x, t_h, t_w])
# @return dst_bbox : 예측된 anchor를 input image 좌표로 변경한 것
# @note RPN을 통해 예측되어 나오는 anchor 박스의 (t_y, t_x, t_h, t_w) 값들은 상대좌표 이다.
###
def get_rois_from_loc_anchors(anchors, rpn_locs):
    """Decode bounding boxes from bounding box offsets and scales.

    Given bounding box offsets and scales computed by
    :meth:`bbox2loc`, this function decodes the representation to
    coordinates in 2D image coordinates.

    Given scales and offsets :math:`t_y, t_x, t_h, t_w` and a bounding
    box whose center is :math:`(y, x) = p_y, p_x` and size :math:`p_h, p_w`,
    the decoded bounding box's center :math:`\\hat{g}_y`, :math:`\\hat{g}_x`
    and size :math:`\\hat{g}_h`, :math:`\\hat{g}_w` are calculated
    by the following formulas.

    * :math:`\\hat{g}_y = p_h t_y + p_y`
    * :math:`\\hat{g}_x = p_w t_x + p_x`
    * :math:`\\hat{g}_h = p_h \\exp(t_h)`
    * :math:`\\hat{g}_w = p_w \\exp(t_w)`

    Args:
        anchors (array): A coordinates of bounding boxes.
            Its shape is :math:`(R, 4)`. These coordinates are
            :math:`p_{ymin}, p_{xmin}, p_{ymax}, p_{xmax}`.
        rpn_locs (array): An array with offsets and scales.
            The shapes of :obj:`anchors` and :obj:`rpn_locs` should be same.
            This contains values :math:`t_y, t_x, t_h, t_w`.

    Returns:
        array:
        Decoded bounding box coordinates. Its shape is :math:`(R, 4)`. \
        The second axis contains four values \
        :math:`\\hat{g}_{ymin}, \\hat{g}_{xmin},
        \\hat{g}_{ymax}, \\hat{g}_{xmax}`.

    """
    src_bbox = anchors
    src_bbox = src_bbox.astype(src_bbox.dtype, copy=False)

    src_height = src_bbox[:, 2] - src_bbox[:, 0]
    src_width = src_bbox[:, 3] - src_bbox[:, 1]
    src_ctr_y = src_bbox[:, 0] + 0.5 * src_height
    src_ctr_x = src_bbox[:, 1] + 0.5 * src_width

    # 상대적인 좌표 예측
    dy = rpn_locs[:, 0]
    dx = rpn_locs[:, 1]
    dh = rpn_locs[:, 2]
    dw = rpn_locs[:, 3]

    dst_y = dy * src_height + src_ctr_y
    dst_x = dx * src_width + src_ctr_x
    dst_h = np.exp(dh) * src_height
    dst_w = np.exp(dw) * src_width

    dst_bbox = np.zeros(rpn_locs.shape, dtype=rpn_locs.dtype)
    dst_bbox[:, 0] = dst_y - 0.5 * dst_h
    dst_bbox[:, 1] = dst_x - 0.5 * dst_w
    dst_bbox[:, 2] = dst_y + 0.5 * dst_h
    dst_bbox[:, 3] = dst_x + 0.5 * dst_w

    return dst_bbox