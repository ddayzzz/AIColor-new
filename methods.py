# coding=utf-8
"""
用于综合上色的所有过程：
1. 风格选择
2. 颜色
"""
import os
import logging

# 这么做的目的是运行不完整配置环境的时候，编辑前端界面
try:
    from cupy.cuda import memory
    import colorInterface
    from styleChanger import generate
    from genColorForAnimation.colorizer import AnimationColorizer
except ImportError:
    pass
except NameError:
    pass


from enum import Enum

__style_model = os.sep.join(('styleChanger', 'models'))
try:
    __animationColorizer = AnimationColorizer(0)
except NameError:
    pass



def error_debug_mode(funcname):
    logging.error(funcname + ': 当前服务器处于调试模式')


class StyleModel(Enum):

    Candy = 'candy_512_2_49000.model'
    Cubist = 'cubist.model'
    Edtaonisl = 'edtaonisl.model'
    Fur = 'fur_0.model'
    Hokusai = 'hokusai.model'
    Hunderwasser = 'hundertwasser.model'
    Kandinsky = 'kandinsky_e2_crop512.model'
    Kanagawa = 'kanagawa.model'
    Scream = "scream-style.model"
    Starrynight = 'starrynight.model'


class ColorizeModel(Enum):

    Normal = 0
    ImageNet = 1  # 值是模型的文件
    Animation = 2  # 动漫风格，使用 PC




def colorizer(imageFile, outImageFile, imageModelEnum):
    """
    彩色化
    :param imageFile: 输入的文件
    :param outImageFile: 输出的文件
    :param imageModelEnum: 采用的模型，是一个对象
    :return:
    """
    try:
        if imageModelEnum == ColorizeModel.Animation:
            __animationColorizer.colorize([imageFile], [outImageFile])
        else:
            colorInterface.generateColorImage(imageFile, outImageFile, imageModelEnum.value)
    except NameError:
        error_debug_mode('colorizer：未加载')
        return False
    except Exception as e:
        logging.error('彩色化图片：{file} 出现异常，预计输出的目标是：{outfile}'.format(file=imageFile, outfile=outImageFile), exc_info=True)
        return False
    logging.info('彩色化图片：{file} 成功，输出的目标是：{outfile}'.format(file=imageFile, outfile=outImageFile))
    return True




def styleChanger(imageFile, outImageFile, model):
    """
    风格化
    :param imageFile: 输入的文件
    :param outImageFile: 输出的文件
    :param model: 采用的风格模型（StyleModel 定义）
    :return:
    """
    try:
        generate.generateImage(imageFile, outImageFile, _model=os.path.sep.join((__style_model, model.value)))
    except NameError as e:
        error_debug_mode('styleChanger：未加载')
        return False
    except Exception as e:
        logging.error('风格化图片：{file} 出现异常，预计输出的目标是：{outfile}'.format(file=imageFile, outfile=outImageFile), exc_info=True)
        return False
    logging.info('风格化图片：{file} 成功，输出的目标是：{outfile}'.format(file=imageFile, outfile=outImageFile))
    return True


if __name__ == '__main__':
    print(os.path.sep.join((__style_model, StyleModel['Candy'])))