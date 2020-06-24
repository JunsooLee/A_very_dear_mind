from pprint import pprint

# @brief Default Configs for training
class Config:
    # data
    voc_data_dir = './data/VOCdevkit/VOC2007'
    min_size = 600  # image resize
    max_size = 1000 # image resize
    num_workers = 4
    test_num_workers =4

    # # sigma for l1_smooth_loss
    rpn_sigma = 3.
    roi_sigma = 1.

    # # param for optimizer
    # # 0.0005 in origin paper but 0.0001 in tf-faster-rcnn
    weight_decay = 0.0005
    lr_decay = 0.1  # 1e-3 -> 1e-4
    lr = 1e-3


    # # visualization
    # env = 'faster-rcnn'  # visdom env
    # port = 8097
    # plot_every = 40  # vis every N iter

    # # preset
    # data = 'voc'
    # pretrained_model = 'vgg16'

    # # training
    epoch = 20


    use_adam = False # Use Adam optimizer & default SGD
    # use_chainer = False # try match everything as chainer
    # use_drop = False # use dropout in RoIHead
    # # debug
    # debug_file = '/tmp/debugf'

    test_num = 20

    # pretrained model path
    load_path = 'D:/PycharmProjects/Faster-RCNN-Pytorch/checkpoints/fasterrcnn_11072246_88%.pth'

    # use caffe pretrained model instead of torchvision
    caffe_pretrain = False
    caffe_pretrain_path = 'checkpoints/vgg16-caffe.pth'

    def _parse(self, kwargs):
        state_dict = self._state_dict()
        for k, v in kwargs.items():
            if k not in state_dict:
                raise ValueError('UnKnown Option: "--%s"' % k)
            setattr(self, k, v)

        print('======user config========')
        pprint(self._state_dict())
        print('==========end============')

    def _state_dict(self):
        return {k: getattr(self, k) for k, _ in Config.__dict__.items() \
                if not k.startswith('_')}


opt = Config()
