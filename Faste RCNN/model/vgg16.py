from torchvision.models import vgg16
from torch import nn

###
# @brief imagenet pretrain vgg16모델 정의 및 상위 4개의 layer 파라미터 고정.
# @return nn.Sequential(*features) : conv layer (마지막 maxpooling layer 제거)
# @return nn.Sequential(*classifier) : FC layer
###
def decom_vgg16():
    model = vgg16(pretrained=True)
    features = list(model.features)[:30]
    classifier = list(model.classifier)
    # @brief remove last layer and dropout layer
    del classifier[6]
    del classifier[5]
    del classifier[2]

    # @brief top layer params 고정
    # @brief Resnet 적용시에도 상위 4개의 layer 고정. (imagenet pretrain 사용)
    for layer in features[:10]:
        for p in layer.parameters():
            p.requires_grad = False
    return nn.Sequential(*features), nn.Sequential(*classifier)