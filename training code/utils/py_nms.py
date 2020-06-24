import numpy as np

###
# @brief Non-Maximum Suppression(NMS): ground truth box와 IoU가 0.7이상 겹치는 anchor 값이 많이 나오기 때문에 하나만 남기고 나머지는 지운다.
# @param rois object가 존재할 상위 12000개의 예측된 anchor 좌표
# @param thresh 0.7
# @return keep : 12000개의 anchor box 중 IoU가 0.7이상인 index return
###
def py_cpu_nms(rois, thresh):
    """
    Pure Python NMS baseline.
    Already Sorted
    
    return:
    keep: roi keep indice
    """
    y1 = rois[:, 0]
    x1 = rois[:, 1]
    y2 = rois[:, 2]
    x2 = rois[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)

    N = len(rois)
    order = np.array(range(N))

    keep = []
    while order.size > 0:
        i = order[0]
        # 겹치는 anchor 중 첫번재 anchor만 저장
        keep.append(i)

        # x1 기준으로 x1좌표가 더 큰 좌표만 계산한다.(a,b의 계산이 b,a에서 다시 계산되는 것 방지)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        # x1,x2(y1, y2)가 서로 역전되지 않는 경우를 생각한다.
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        # ovr: anchor끼리의 IoU
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= thresh)[0]
        order = order[inds + 1]

    return keep