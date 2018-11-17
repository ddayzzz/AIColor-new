import logging
import numpy as np
import chainer
from chainer import cuda, serializers, Variable  # , optimizers, training
import cv2
import os.path
from genColorForAnimation.imageDataset import ImageAndRefDataset
from genColorForAnimation import unet, lnet


class AnimationColorizer:

    def log_debug(self, msg):
        logging.debug('AnimationColorizer:' + msg)

    def log_error(self, msg):
        logging.error('AnimationColorizer:' + msg)

    def __init__(self, gpu=0):
        self.log_debug('加载模型...')
        self.batchsize = 1
        self.gpu = gpu
        self._dtype = np.float32

        if not os.path.isfile("./genColorForAnimation/models/unet_128_standard"):
            self.log_error('无法加载模型“./genColorForAnimation/models/unet_128_standard”')
            return
        if not os.path.isfile("./genColorForAnimation/models/unet_512_standard"):
            self.log_error('无法加载模型“./genColorForAnimation/models/unet_512_standard”')
            return
        self.log_debug('成功加载模型')

        if self.gpu >= 0:
            self.log_debug('使用GPU: %d' % gpu)
            cuda.get_device(self.gpu).use()
            cuda.set_max_workspace_size(64 * 1024 * 1024)  # 64MB
            chainer.Function.type_check_enable = False
        self.cnn_128 = unet.UNET()
        self.cnn_512 = unet.UNET()
        if self.gpu >= 0:
            self.cnn_128.to_gpu()
            self.cnn_512.to_gpu()
        serializers.load_npz(
            "./genColorForAnimation/models/unet_128_standard", self.cnn_128)
        serializers.load_npz(
            "./genColorForAnimation/models/unet_512_standard", self.cnn_512)


    def save_as_img(self, array, name):
        """
        保存图像到图像文件
        :param array: 图像数组
        :param name: 文件名
        :return:
        """
        array = array.transpose(1, 2, 0)
        array = array.clip(0, 255).astype(np.uint8)
        array = cuda.to_cpu(array)
        (major, minor, _) = cv2.__version__.split(".")
        if major == '3':
            img = cv2.cvtColor(array, cv2.COLOR_YUV2RGB)
        else:
            img = cv2.cvtColor(array, cv2.COLOR_YUV2BGR)
        cv2.imwrite(name, img)


    def colorize(self, in_imgFilePaths, out_imgFilePaths, usingCNN512=False, blur=0, s_size=128):
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()

        dataset = ImageAndRefDataset(in_imgFilePaths)

        sample = dataset.get_example(0, minimize=True, blur=blur, s_size=s_size)

        sample_container = np.zeros(
            (1, 4, sample[0].shape[1], sample[0].shape[2]), dtype='f')
        sample_container[0, :] = sample[0]

        if self.gpu >= 0:
            sample_container = cuda.to_gpu(sample_container)

        cnn = {True: self.cnn_512, False: self.cnn_128}
        with chainer.no_backprop_mode():
            with chainer.using_config('train', False):
                image_conv2d_layer = cnn[usingCNN512].calc(Variable(sample_container))
        del sample_container

        input_bat = np.zeros((1, 4, sample[1].shape[1], sample[1].shape[2]), dtype='f')
        print(input_bat.shape)
        input_bat[0, 0, :] = sample[1]

        output = cuda.to_cpu(image_conv2d_layer.data[0])
        del image_conv2d_layer  # release memory

        for channel in range(3):
            input_bat[0, 1 + channel, :] = cv2.resize(
                output[channel, :],
                (sample[1].shape[2], sample[1].shape[1]),
                interpolation=cv2.INTER_CUBIC)

        if self.gpu >= 0:
            link = cuda.to_gpu(input_bat, None)
        else:
            link = input_bat
        with chainer.no_backprop_mode():
            with chainer.using_config('train', False):
                image_conv2d_layer = self.cnn_512.calc(Variable(link))
        del link  # release memory

        self.save_as_img(image_conv2d_layer.data[0], out_imgFilePaths[0])
        del image_conv2d_layer



if __name__ == '__main__':
    for n in range(1):
        p = AnimationColorizer()
        print(n)
        p.colorize(['genColorForAnimation/1.jpg'], ['2.jpg'], False)
