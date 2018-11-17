# coding=utf-8
#

import numpy as np
import chainer
import os
import cv2
import logging


def cvt2YUV(img):
    (major, minor, _) = cv2.__version__.split(".")
    if major == '3':
        img = cv2.cvtColor( img, cv2.COLOR_RGB2YUV )
    else:
        img = cv2.cvtColor( img, cv2.COLOR_BGR2YUV )
    return img


class ImageAndRefDataset(chainer.dataset.DatasetMixin):

    def __init__(self, paths, dtype=np.float32):
        """
        构建图像数据
        :param paths: 图像的文件名
        :param prefix: 图像的前缀文件路径
        :param dtype: 类型
        """
        self._paths = paths
        self._dtype = dtype

    def __len__(self):
        return len(self._paths)

    def get_name(self, i):
        return self._paths[i]

    def get_example(self, i, minimize=False, blur=0, s_size=128):
        path1 = self._paths[i]
        image1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        logging.debug("AnimationColorizer: 加载图片：" + path1)
        image1 = np.asarray(image1, self._dtype)

        _image1 = image1.copy()
        if minimize:
            if image1.shape[0] < image1.shape[1]:
                s0 = s_size
                s1 = int(image1.shape[1] * (s_size / image1.shape[0]))
                s1 = s1 - s1 % 16
                _s0 = 4 * s0
                _s1 = int(image1.shape[1] * ( _s0 / image1.shape[0]))
                _s1 = (_s1+8) - (_s1+8) % 16
            else:
                s1 = s_size
                s0 = int(image1.shape[0] * (s_size / image1.shape[1]))
                s0 = s0 - s0 % 16
                _s1 = 4 * s1
                _s0 = int(image1.shape[0] * ( _s1 / image1.shape[1]))
                _s0 = (_s0+8) - (_s0+8) % 16

            _image1 = image1.copy()
            _image1 = cv2.resize(_image1, (_s1, _s0),
                                 interpolation=cv2.INTER_AREA)

            if blur > 0:
                blured = cv2.blur(_image1, ksize=(blur, blur))
                image1 = _image1 + blured - 255

            image1 = cv2.resize(image1, (s1, s0), interpolation=cv2.INTER_AREA)

        # image is grayscale
        if image1.ndim == 2:
            image1 = image1[:, :, np.newaxis]
        if _image1.ndim == 2:
            _image1 = _image1[:, :, np.newaxis]

        image1 = np.insert(image1, 1, -512, axis=2)
        image1 = np.insert(image1, 2, 128, axis=2)
        image1 = np.insert(image1, 3, 128, axis=2)


        return image1.transpose(2, 0, 1), _image1.transpose(2, 0, 1)
