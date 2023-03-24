import json
import torch
import numpy as np
import os
import PIL
from PIL import Image


def is_json(f):
    return f.endswith('json')


def make_dataset(path, dir, val_ratio=0.05):
    train_img = []
    train_y = []
    test_img = []
    test_y = []

    file_list = os.listdir(path + dir)
    file_list = filter(is_json, file_list)
    file_list = [os.path.join(path + dir, f) for f in file_list]
    file_list.sort()
    print('There are {} samples'.format(len(file_list)))

    num_training_sample = 0
    num_testing_sample = 0
    for i, fn in enumerate(file_list):
        with open(fn) as f:
            data = json.load(f)
        img = Image.open(os.path.join(path, data['image_path']))
        img = img.resize((224, 224), PIL.Image.ANTIALIAS)
        img = np.asarray(img)
        img = img.reshape([3, 224, 224])
        target_location = data['target_location']
        if len(target_location) == 0:
            target_location = [0, 0]
            label = 0
        else:
            label = 1

        if i > len(file_list) * val_ratio:
            train_img.append(img)
            train_y.append([label, target_location[0], target_location[1]])
            num_training_sample += 1
        else:
            test_img.append(img)
            test_y.append([label, target_location[0], target_location[1]])
            num_testing_sample += 1

    train_x = torch.from_numpy(np.array(train_img)).float()
    train_y = torch.from_numpy(np.array(train_y)).float()
    test_x = torch.from_numpy(np.array(test_img)).float()
    test_y = torch.from_numpy(np.array(test_y)).float()
    return train_x, train_y, test_x, test_y


if __name__ == '__main__':
    path = '/home/zoker/COMP6445/Group_project/collect_data'
    dir = '/random_dataset_V0'
    train_x, train_y, test_x, test_y = make_dataset(path, dir)
    print(test_y[:, 0])