import os

import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data import DataLoader, Dataset

import captcha.dataset.encoding as ohe
import captcha.cnn.setting as setting


class MyDataSet(Dataset):
    def __init__(self, folder, transform=None):
        self.train_image_file_paths = [os.path.join(folder, image_file) for image_file in os.listdir(folder)]
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.repeat(1, 1, 1)),
            # transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
        ])

    def __len__(self):
        return len(self.train_image_file_paths)

    def __getitem__(self, idx):
        image_root = self.train_image_file_paths[idx]
        image_name = image_root.split(os.path.sep)[-1]

        image = Image.open(image_root)
        if self.transform is not None:
            image = self.transform(image)
        # 为了方便，在生成图片的时候，图片文件的命名格式 "4个数字或者数字_时间戳.PNG", 4个字母或者即是图片的验证码的值，字母大写,同时对该值做 one-hot 处理
        label = ohe.encode(image_name.split('_')[0])
        return image, label


class SingleData(Dataset):
    def __init__(self, image=Image.Image, transform=None):
        self.image = image
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.repeat(1, 1, 1)),
            # transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
        ])

    def __len__(self):
        return 1

    def __getitem__(self, idx):
        img = self.image
        if self.transform is not None:
            img = self.transform(img)
        # 为了方便，在生成图片的时候，图片文件的命名格式 "4个数字或者数字_时间戳.PNG", 4个字母或者即是图片的验证码的值，字母大写,同时对该值做 one-hot 处理
        label = ohe.encode('aaaa')
        return img, label


transform = transforms.Compose([
    transforms.ColorJitter(),
    # transforms.Grayscale(),
    transforms.ToTensor(),
    # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def train_data_loader():
    dataset = MyDataSet(setting.TRAIN_DATASET_PATH, transform=transform)
    return DataLoader(dataset, batch_size=64, shuffle=True)


def eval_data_loader():
    dataset = MyDataSet(setting.EVAL_DATASET_PATH, transform=transform)
    return DataLoader(dataset, batch_size=1, shuffle=True)


def predict_datas_loader():
    dataset = MyDataSet(setting.PREDICT_DATASET_PATH, transform=transform)
    return DataLoader(dataset, batch_size=1, shuffle=True)


def predict_single_data_loader(img=Image.Image):
    dataset = SingleData(img, transform=transform)
    return DataLoader(dataset, batch_size=1, shuffle=True)
