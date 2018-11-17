from __future__ import print_function
import numpy as np
import argparse
from PIL import Image, ImageFilter
import time
import os
import chainer
from chainer import cuda, Variable, serializers
from styleChanger.net import *


# 缓存机制，目前采用CPU的模式
_loaded_modles = dict()


def _loadModelFromFile(modelFile, gpu):
    model = FastStyleNet()  # 使用的模型
    serializers.load_npz(modelFile, model)  # 选取载入的模型
    if gpu >= 0:
        cuda.get_device(gpu).use()
        model.to_gpu()
    _loaded_modles[modelFile] = model


def _getLoadedModel(modelFile, gpu):
    if not _loaded_modles.get(modelFile, None):
        # 加载
        _loadModelFromFile(modelFile, gpu)
    return _loaded_modles[modelFile]
    


def original_colors(original, stylized):
    h, s, v = original.convert('HSV').split()
    hs, ss, vs = stylized.convert('HSV').split()
    return Image.merge('HSV', (h, s, vs)).convert('RGB')




def generateImage(input, output, _model, keep_colors=False, gpu=-1, median_filter=3, padding=38):
    """
    生成按照指定画风的图片
    :param input: 输入的图片文件
    :param output: 输出的文件：返回的是相对地址
    :param _model: 采用的模型的文件，在models中定义
    :param keep_colors: 是否保持原素描画的颜色
    :param gpu: 使用GPU的编号，-1表示cpu
    :param median_filter: 中间层
    :param padding: 展开的填充
    :return:
    """
    # model = FastStyleNet()  # 使用的模型
    # serializers.load_npz(_model, model)  # 选取载入的模型
    # if gpu >= 0:
    #     cuda.get_device(gpu).use()
    #     model.to_gpu()
    model = _getLoadedModel(_model, gpu)
    xp = np if gpu < 0 else cuda.cupy
    
    start = time.time()
    original = Image.open(input).convert('RGB')
    image = np.asarray(original, dtype=np.float32).transpose(2, 0, 1)
    image = image.reshape((1,) + image.shape)
    if padding > 0:
        image = np.pad(image, [[0, 0], [0, 0], [padding, padding], [padding, padding]], 'symmetric')
    image = xp.asarray(image)
    x = Variable(image)

    y = model(x)
    result = cuda.to_cpu(y.data)

    if padding > 0:
        result = result[:, :, padding:-padding, padding:-padding]
    result = np.uint8(result[0].transpose((1, 2, 0)))
    med = Image.fromarray(result)
    if median_filter > 0:
        med = med.filter(ImageFilter.MedianFilter(median_filter))
    if keep_colors:
        med = original_colors(original.resize((med.size), 3), med)

    med.save(output)
    if not os.path.exists(output):
        raise FileNotFoundError('没有找到对应的生成的文件：%s' % output)
    return time.time() - start


if __name__ == '__main__':
    # 静物系列
    print(generateImage('sample_images/sm_jw.jpg',
                        'sample_images/sm_starrynight_jw.jpg',
                        'models/starrynight.model',
                        gpu=-1))
    print(generateImage('sample_images/sm_jw.jpg',
                        'sample_images/sm_scream-style_jw.jpg',
                        'models/scream-style.model',
                        gpu=-1))
    print(generateImage('sample_images/sm_jw.jpg',
                        'sample_images/sm_kanagawa_jw.jpg',
                        'models/kanagawa.model',
                        gpu=-1))