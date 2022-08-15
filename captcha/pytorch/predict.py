import os

import numpy as np
import torch
from PIL import Image
from torch.autograd import Variable

import captcha.cnn.setting as setting
import captcha.cnn.model as model
from captcha.dataset import dataset


# from cnn import setting,dataset,cnn as CNN


def get(img=Image.Image):
    cnn = model.CNN()
    cnn.eval()

    # 加载最佳模型
    cnn.load_state_dict(torch.load('./captcha/model/cnn_last.pt', map_location=torch.device('cpu')))

    # 加载图片
    # predict_dataloader = dataset.get_predict_datas_loader()
    predict_dataloader = dataset.predict_single_data_loader(img)

    # vis = Visdom(use_incoming_socket=False)
    for i, (images, labels) in enumerate(predict_dataloader):
        image = images
        vimage = Variable(image)
        predict_label = cnn(vimage)

        # 预测标签
        c0 = setting.ALL_CHAR_SET[np.argmax(predict_label[0, 0:setting.ALL_CHAR_SET_LEN].data.numpy())]
        c1 = setting.ALL_CHAR_SET[np.argmax(
            predict_label[0, setting.ALL_CHAR_SET_LEN:2 * setting.ALL_CHAR_SET_LEN].data.numpy())]
        c2 = setting.ALL_CHAR_SET[np.argmax(
            predict_label[0, 2 * setting.ALL_CHAR_SET_LEN:3 * setting.ALL_CHAR_SET_LEN].data.numpy())]
        c3 = setting.ALL_CHAR_SET[np.argmax(
            predict_label[0, 3 * setting.ALL_CHAR_SET_LEN:4 * setting.ALL_CHAR_SET_LEN].data.numpy())]

        c = '%s%s%s%s' % (c0, c1, c2, c3)
        # print(c)
        return c
        # vis.images(image, opts=dict(caption=c))
