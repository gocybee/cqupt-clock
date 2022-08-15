import numpy as np
import torch
from torch.autograd import Variable

from captcha.cnn.model import *
from captcha.dataset import dataset
from captcha.dataset import encoding

# os.environ["CUDA_VISIBLE_DEVICES"] = "1"

device = torch.device("cpu")


def test_data(model_path):
    cnn = CNN()
    cnn.eval()
    # 加载模型
    cnn.load_state_dict(torch.load(model_path, map_location=device))

    # 加载评价数据集
    test_dataloader = dataset.eval_data_loader()

    correct = 0
    total = 0

    for i, (images, labels) in enumerate(test_dataloader):

        image = images
        vimage = Variable(image)
        predict_label = cnn(vimage)

        # 获取预测标签
        c0 = setting.ALL_CHAR_SET[np.argmax(predict_label[0, 0:setting.ALL_CHAR_SET_LEN].data.numpy())]
        c1 = setting.ALL_CHAR_SET[
            np.argmax(predict_label[0, setting.ALL_CHAR_SET_LEN:2 * setting.ALL_CHAR_SET_LEN].data.numpy())]
        c2 = setting.ALL_CHAR_SET[
            np.argmax(predict_label[0, 2 * setting.ALL_CHAR_SET_LEN:3 * setting.ALL_CHAR_SET_LEN].data.numpy())]
        c3 = setting.ALL_CHAR_SET[
            np.argmax(predict_label[0, 3 * setting.ALL_CHAR_SET_LEN:4 * setting.ALL_CHAR_SET_LEN].data.numpy())]
        predict_label = '%s%s%s%s' % (c0, c1, c2, c3)

        # 校验标签
        true_label = encoding.decode(labels.numpy()[0])
        total += labels.size(0)
        if predict_label == true_label:
            correct += 1

        # if(total%200==0):
        # print('Test Accuracy of the cnn on the %d test images: %f %%' % (total, 100 * correct / total))
    # print('Test Accuracy of the cnn on the %d test images: %f %%' % (total, 100 * correct / total))
    return 100 * correct / total
