import time
from enum import Enum
from methods import StyleModel, ColorizeModel
import uuid
from aiohttp import web

import logging
import inspect
from urllib import parse
from pymysql.err import InternalError
import os
import models

# 定义处理图片的大小
UploadImageMaxWidth = 1024
UploadImageMaxHeight = 768

_upload_dir = os.sep.join(('gallery', 'upload'))
_styled_dir = os.sep.join(('gallery', 'styled'))
_colorized_dir = os.sep.join(('gallery', 'colorized'))


class RouterCallBack(object):

    def __init__(self, router):
        self.router = router

    async def __call__(self, request):
        # 获取函数的参数表
        required_args = inspect.signature(self.router).parameters
        # logger.get_logger().info('需要的参数: %s' % required_args)
        # 获取从GET或POST传进来的参数值，如果函数参数表有这参数名就加入
        if request.method == 'POST':
            # for k in dir(request):
            #     print(k + ':' + str(getattr(request, k)))
            if getattr(request, '__data__', None):
                kw = {arg: value for arg, value in request.__data__.items() if
                      arg in required_args}  # POST需要进行参数的一些转换，这个转换在data工厂中。数据存储在__data__属性中
            else:
                kw = dict()  # 只有传递了数据才会有__data__
        else:
            # GET参数有可能需要类似于http://xxx.com/blog?id=5&name=ff之类的参数
            qs = request.query_string
            if qs:
                # logger.get_logger().info('GET指令的query参数: %s' % request.query_string)
                kw = {arg: value if isinstance(value, list) and len(value) > 1 else value[0] for arg, value in
                      parse.parse_qs(qs,
                                     True).items()}  # 保留空格。将查询参数添加到kw已知的参数列表 ref https://raw.githubusercontent.com/icemilk00/Python_L_Webapp/master/www/coroweb.py。可以支持传递数组
            else:
                kw = {arg: value for arg, value in request.match_info.items() if arg in required_args}
        # 获取match_info的参数值，例如@get('/blog/{id}')之类的参数值
        kw.update(request.match_info)
        # 如果有request参数的话也加入
        if 'request' in required_args:
            kw['request'] = request
        # 如果需要 websocket 通信
        # if self.router.level == 'websocket' and 'wsResponse' in required_args:
        #     ws = web.WebSocketResponse()
        #     await ws.prepare(request)
        #     kw['wsResponse'] = ws  # 使用异步 for 就可以得出消息
        # 检查参数表中有没参数缺失
        for key, arg in required_args.items():
            # request参数不能为可变长参数
            if key == 'request' and arg.kind in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                return web.HTTPBadRequest(text='request 参数不能是可变参数')
            # 如果参数类型不是变长列表和变长字典，变长参数是可缺省的
            if arg.kind not in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                # 如果还是没有默认值，而且还没有传值的话就报错
                if arg.default == arg.empty and arg.name not in kw:
                    raise ValueError('缺少的参数: %s' % arg.name)

        logging.info('使用参数 {paras} 调用路由：{method} {path} 关联的函数'.format(paras=kw, method=request.method, path=request.path))
        return await self.router(**kw)


def getImageFilePath(imgSource, imageid, **kwargs):
    """
    获取文件的路径
    :param imgSource: 来源
    :param imageid: 图像ID
    :param kwargs: 其他参数
    :return:
    """
    if imgSource == ImageSource.Upload:
        return os.sep.join((_upload_dir, imageid))
    elif imgSource == ImageSource.Colorized:
        return os.sep.join((_colorized_dir, imageid))
    elif imgSource == ImageSource.Styled:
        return os.sep.join((_styled_dir, imageid))


async def getTargetImageByIdAndSource(dbm, imageId, sourceIndexEnum, modelFieldName, modelValue, targetModel):
    """
    获取与来源图片id和指定模型
    :param dbm: 数据库连接对象
    :param imageId: 原图片ID
    :param sourceIndexEnum: 原图片来源的索引
    :param modelFieldName: 采用的格式化的模型在targetModel关联的表中的属性名
    :param modelValue: 格式化的模型的值
    :param targetModel: 需要得到的ORM模型元类子类
    :return:
    """
    sql_where = '`originalImageId`=? and `imageSourceIndex`=? and `%s`=?' % modelFieldName
    sql_paras = [imageId, sourceIndexEnum.value, modelValue]
    return await dbm.queryAll(sql_where=sql_where, args=sql_paras, model_type=targetModel)


async def getImageFileInDB(dbm, imgSrcEnum, imgid):
    """
    获取数据库中登记的图片信息
    :param dbm: 数据库
    :param imgSrcEnum: 来源的  enum 对象
    :param imgid: 图像ID
    :return:
    """
    try:
        if imgSrcEnum == ImageSource.Upload:
            return await dbm.queryAll(models.UploadedImage, 'imageId=?',
                                      (imgid,))  # 用户名也必须匹配
        elif imgSrcEnum == ImageSource.Colorized:
            return await dbm.queryAll(models.ColorizedImage, 'imageId=?', (imgid,))
        elif imgSrcEnum == ImageSource.Styled:
            return await dbm.queryAll(models.StyledImage, 'imageId=?', (imgid,))
        return None
    except InternalError:  # 如果数据指定失败了，就直接返回空而不是报错
        return None


class ImageSource(Enum):

    Upload = 0
    Styled = 1
    Colorized = 2


def next_id():
    return '%010d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


def get_loggined_username_or_denied(request):
    if not request.__user__:
        raise web.web_exceptions.HTTPForbidden()
    else:
        return request.__user__.username


def just_get_username(request):
    return request.__user__.username if request.__user__ else None


avaiableModels = {
    ImageSource.Styled.value: [
        {
            'name': StyleModel.Candy.name,
            'desc': "Candy 画派",
            'image': '/static/images/styled/candy-style.jpg'
        },
        {
            'name': StyleModel.Cubist.name,
            'desc': '立体主义',
            'image': '/static/images/styled/cubist-style.jpg'
        },
        {
            'name': StyleModel.Edtaonisl.name,
            'desc': 'Edtaonisl 画派',
            'image': '/static/images/styled/edtaonisl-style.jpg'
        },
        {
            'name': StyleModel.Fur.name,
            'desc': "Fur 画派",
            'image': '/static/images/styled/fur-style.jpg'
        },
        {
            'name': StyleModel.Hokusai.name,
            'desc': '葛饰北斋-浮士绘',
            'image': '/static/images/styled/hokusai-style.jpg'
        },
        {
            'name': StyleModel.Hunderwasser.name,
            'desc': '奥地利建筑风格',
            'image': '/static/images/styled/hundertwasser-style.jpg'
        },
        {
            'name': StyleModel.Kanagawa.name,
            'desc': 'Edtaonisl 画派',
            'image': '/static/images/styled/kanagawa-style.jpg'
        },
        {
            'name': StyleModel.Kandinsky.name,
            'desc': "康定斯基风格",
            'image': '/static/images/styled/kandinsky-style.jpg'
        },
        {
            'name': StyleModel.Scream.name,
            'desc': '爱德华·孟克-呐喊',
            'image': '/static/images/styled/scream-style.jpg'
        },
        {
            'name': StyleModel.Starrynight.name,
            'desc': '星·夜-梵·高',
            'image': '/static/images/styled/starrynight-style.jpg'
        }
    ],
    ImageSource.Colorized.value:[
        {
            'name': ColorizeModel.Animation.name,
            'desc': '适合于动画',
            'image': '/static/images/colored/animation.jpg'
        },
        {
            'name': ColorizeModel.ImageNet.name,
            'desc': 'ImageNet 模型',
            'image': '/static/images/colored/imagenet.jpg'
        },
        {
            'name': ColorizeModel.Normal.name,
            'desc': '适合于普通图片',
            'image': '/static/images/colored/normal.jpg'
        }
    ]
}

avaiableModelsForBrowser = {
    ImageSource.Styled.value:[
        {
            'id': 0,
            'name': 'Des Glaneuses',
            'desc': 'Des Glaneuses - 拾穗者，让-弗朗索瓦·米勒',
            'image128': 'static/images/onBrowser/128/style1.jpg',
            'image256': 'static/images/onBrowser/256/style1.jpg',
            'modelJsonUrl': 'templates/genStyleOnBrowser/style1/model.json'
        },
        {
            'id': 1,
            'name': 'La Muse',
            'desc': 'La Muse - 毕加索',
            'image128': 'static/images/onBrowser/128/style2.jpg',
            'image256': 'static/images/onBrowser/256/style2.jpg',
            'modelJsonUrl': 'templates/genStyleOnBrowser/style2/model.json'
        },
        {
            'id': 2,
            'name': 'Mirror',
            'desc': 'Mirror - 镜子前的女孩，毕加索',
            'image128': 'static/images/onBrowser/128/style3.jpg',
            'image256': 'static/images/onBrowser/256/style3.jpg',
            'modelJsonUrl': 'templates/genStyleOnBrowser/style3/model.json'
        },
        {
            'id': 3,
            'name': 'Udnie',
            'desc': 'Udnie - 弗朗西斯·毕卡比亚',
            'image128': 'static/images/onBrowser/128/style4.jpg',
            'image256': 'static/images/onBrowser/256/style4.jpg',
            'modelJsonUrl': 'templates/genStyleOnBrowser/style4/model.json'
        },
        {
            'id': 4,
            'name': 'Wave',
            'desc': 'Wave - 浮士绘，葛饰北斋',
            'image128': 'static/images/onBrowser/128/style5.jpg',
            'image256': 'static/images/onBrowser/256/style5.jpg',
            'modelJsonUrl': 'templates/genStyleOnBrowser/style5/model.json'
        }
    ]
}