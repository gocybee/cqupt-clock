# -*- coding: UTF-8 -*-
import argparse
import shutil

import torch
from torch.autograd import Variable

import evaluate
import torch_util
from captcha.cnn.model import *
from captcha.dataset import dataset

# os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

# 训练参数

num_epochs = 100
batch_size = 32
learning_rate = 0.001

# device = pytorch.device("cpu") # 仅使用CPU
device = torch_util.select_device()  # 优先使用显卡,其次使用CPU


def main(model_args):
    cnn = CNN().to(device)

    cnn.train()
    criterion = nn.MultiLabelSoftMarginLoss()
    # 设置优化算法为Adam
    optimizer = torch.optim.Adam(cnn.parameters(), lr=learning_rate)

    # 加载模型
    if model_args.resume:
        cnn.load_state_dict(torch.load(model_args.model_path, map_location=device))

    max_acc = 0  # 设置最大准确度为0
    # 加载训练数据集
    train_dataloader = dataset.train_data_loader()
    # 创建存储可视化数据的文本文件(附加读写模式)
    result_file = open('../model/result.txt', 'w+', encoding='utf-8')
    # 清空文本内容
    # result_file.truncate(0)

    # 循环 num_epochs 次
    for epoch in range(num_epochs):
        for i, (images, labels) in enumerate(train_dataloader):
            # 设置入参
            images = Variable(images).to(device)
            # 设置标签
            labels = Variable(labels.float()).to(device)
            # 获取预测标签
            predict_labels = cnn(images)
            # 获取loss
            loss = criterion(predict_labels, labels)
            # 清除所有优化的张量的梯度
            optimizer.zero_grad()
            # 反向传播
            loss.backward()
            # 更新步数
            optimizer.step()
            if (i + 1) % 2 == 0:
                print("epoch: %03g \t step: %03g \t loss: %.5f \t\r" % (epoch, i + 1, loss.item()))
                torch.save(cnn.state_dict(), "../model/cnn_%03g.pt" % epoch)
        print("epoch: %03g \t step: %03g \t loss: %.5f \t" % (epoch, i, loss.item()))

        torch.save(cnn.state_dict(), "../model/cnn_%03g.pt" % epoch)
        # 评价模型
        acc = evaluate.test_data("../model/cnn_%03g.pt" % epoch)
        # 保存最佳模型
        if max_acc < acc:
            print("update accuracy %.5f." % acc)
            max_acc = acc
            shutil.copy("../model/cnn_%03g.pt" % epoch, "../model/cnn_best.pt")
        else:
            print("do not update %.5f." % acc)
        # 存储每次迭代的效果数据
        result_file.write('%s,%s\n' % (epoch, max_acc))
    torch.save(cnn.state_dict(), "../model/cnn_last.pt")
    print("save last cnn")
    result_file.close()
    torch_util.plot_result('../model/result.txt')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="load path")
    parser.add_argument('--model-path', type=str, default="../model/cnn_0.pt")
    parser.add_argument('--resume', action='store_true')

    args = parser.parse_args()
    main(args)
