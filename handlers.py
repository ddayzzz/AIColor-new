# coding=utf-8
"""
定义处理服务端的各种路由处理工具
数据库：aicolor
用户：aitest
密码：test123
"""
import os
import logging
import models
import methods
from aiohttp import web
from bases import ImageSource, next_id, avaiableModels, getImageFilePath, getTargetImageByIdAndSource, getImageFileInDB
from bases import UploadImageMaxHeight, UploadImageMaxWidth

from socialHandlers import _get_postId as get_postId  # 获取某个图片的关联ID
# 图像中间处理
from io import BytesIO
from PIL import Image




async def store_upload_images(request):
    """
    存储用户上传的文件，可以上传对各文件
    :param request: 是一个用户的请求
    :param typeName: 指定的文件类型
    :return: 返回所有上传的文件的Id. 对应的文件可以在指定的目录下找到
    """
    if not request.__user__:
        return 403
    else:
        username = request.__user__.username
    reader = await request.multipart()
    file = await reader.next()
    res = []
    while file:
        # ext = str.lower(file.filename[file.filename.rfind('.'):])
        imageId = next_id()  # 不再处理格式
        save_prefix = getImageFilePath(ImageSource.Upload, imageId)
        # 保存为完整的文件流
        # with open(target, 'wb') as f:
        #     while True:
        #         chunk = await file.read_chunk()
        #         if not chunk:
        #             break
        #         f.write(chunk)
        imageFileStream = BytesIO()  # 载入内存
        while True:
            chunk = await file.read_chunk()
            if not chunk:
                break
            imageFileStream.write(chunk)
        imageFileStream.seek(0)
        # 创建 Image
        sImg = Image.open(imageFileStream)
        w, h = sImg.size
        # 检查大小信息
        if w > UploadImageMaxWidth or h > UploadImageMaxHeight:
            # 需要按比例缩放
            ratio = float(w) / h
            newSize = (int(UploadImageMaxWidth * ratio), int(UploadImageMaxHeight * ratio))
            sImg = sImg.resize(newSize,Image.ANTIALIAS)
            logging.debug('转换图片：(%d, %d) -> (%d, %d)' % (w,h,newSize[0], newSize[1]))
        # 格式转换
        if sImg.mode != 'RGB':
            sImg = sImg.convert('RGB')
            logging.debug('转换图片格式到RGB')
        # 保存到文件
        imageId = imageId + '.jpg'
        sImg.save(save_prefix + '.jpg', quality=95)
        res.append(imageId)
        file = await reader.next()
    # 存储到数据库中
    dbm = request.__dbManager__
    # 上传的都是新的
    for imageId in res:
        obj = models.UploadedImage(username=username, imageId=imageId)
        await dbm.insert(obj)
    return {
        'imagesIds': res
    }


# @routes.get('/api/v1/getStyled') # originalImageId={originalImageId}&styledModel={styledModel}&originalImageIndex={originalImageIndex}
async def process_styled_image(request, originalImageId, styledModel, originalImageIndex):


    model = styledModel  # 定义的模型
    imageId = originalImageId  # 任何图片的Id。如果存在就不进行特殊化，直接返回指定的文件的ImageId
    _originalImageIndex = originalImageIndex
    returnData = {
        'originalImageId': imageId,
        'originalImageIndex': _originalImageIndex,
        'styledModel': None,
        'messages': '%s 不存在' % imageId,
        'imageId': None,
        'status': 1,
        'cached': False,
        'postId': None  # 关联的 postId. 只有 cached == true 才会设置
    }
    if not request.__user__:
        returnData['messages'] = '没有指定进行风格化操作的用户名'
        return returnData
    else:
        username = request.__user__.username
    try:
        model_code = methods.StyleModel[model]
    except KeyError:
        returnData['messages'] = '未知的风格化模型参数：%s' % model
        return returnData

    try:
        originalImageIndex = ImageSource(int(_originalImageIndex))
    except ValueError:
        returnData['messages'] = '图像来源类型错误：%s' % _originalImageIndex
        return returnData

    # 从数据库中读取
    dbm = request.__dbManager__
    # 检查是否存在
    mayExists = await getTargetImageByIdAndSource(dbm, imageId, originalImageIndex, 'styledModel', model,models.StyledImage)
    if len(mayExists) > 0:  # 保证只会存在一个
        returnData['messages'] = '使用已经创建的风格化图片'
        returnData['styledModel'] = model
        returnData['imageId'] = mayExists[0].imageId
        returnData['status'] = 0
        returnData['cached'] = True
        # 检查是否有关联的 postID
        returnData['postId'] = await get_postId(dbm, mayExists[0].imageId)
        return returnData
    # 获取图片源的位置
    originalImgFile = getImageFilePath(originalImageIndex, imageid=imageId)  # 原始图片的类型
    originalImgObj = None
    if originalImageIndex == ImageSource.Upload:
        originalImgObj = await dbm.query(models.UploadedImage, imageId=imageId)
    elif originalImageIndex == ImageSource.Colorized:
        originalImgObj = await dbm.query(models.ColorizedImage, imageId=imageId)
    else:
        originalImgObj = await dbm.query(models.StyledImage, imageId=imageId)
    # 检查是否存在原文件
    if not os.path.exists(originalImgFile) or not originalImgObj:
        returnData['messages'] = '指定的图片ID对应的文件或记录不存在：%s' % imageId
        return returnData
    # 风格
    ext = imageId[imageId.rfind('.'):]
    styledImageId = next_id() + ext
    styledImageFile = getImageFilePath(ImageSource.Styled, styledImageId)
    res = methods.styleChanger(originalImgFile, styledImageFile, model=model_code)
    if not res:
        returnData['messages'] = '没有生成指定的风格化图片：%s' %  styledImageFile
        return returnData
    # 存入数据库
    await dbm.insert(
        models.StyledImage,
        imageId=styledImageId,
        originalImageId=imageId,
        styledModel=model,
        username =username,
        imageSourceIndex=originalImageIndex.value
    )
    # styledImagesItem = await dbm.query(models.StyledImage, uploadImageId=imageId, styledModel=model)
    #
    # # 目标文件
    # if not styledImagesItem or not os.path.exists(targetFile):
    #     # 还没有渲染过
    #     if not os.path.exists(targetFile):
    #         methods.styleChanger(getImageFilePath(_upload_dir, imageId),
    #                              targetFile, model=model_code)
    # # 存入数据库
    # if not styledImagesItem:
    #     await dbm.insert(models.StyledImage, uploadImageId=imageId, styledModel=model)
    returnData['messages'] = '成功风格化图像'
    returnData['styledModel'] = model
    returnData['imageId'] = styledImageId
    returnData['status'] = 0
    return returnData



# @routes.get('/api/v1/getColorized', name='get_colorized')  # originalImageId={originalImageId}&colorizedModel={colorizedModel}&originalImageIndex={originalImageIndex}
async def process_colorized_image(request, originalImageId, colorizedModel, originalImageIndex):


    model = colorizedModel  # 定义的模型
    imageId = originalImageId  # 任何图片的Id。如果存在就不进行特殊化，直接返回指定的文件的ImageId
    returnData = {
        'originalImageId': imageId,
        'originalImageIndex': originalImageIndex,
        'colorizedModel': None,
        'messages': '%s 不存在' % imageId,
        'imageId': None,
        'status': 1,
        'cached': False,
        'postId': None
    }
    if not request.__user__:
        returnData['messages'] = '没有指定进行上色操作的用户名'
        return returnData
    else:
        username = request.__user__.username
    # 检查彩色化的模型
    try:
        model_code = methods.ColorizeModel[model]
    except KeyError:
        returnData['messages'] = '未知的彩色化模型参数：%s' % model
        return returnData

    try:
        originalImageIndex = ImageSource(int(originalImageIndex))
    except ValueError:
        returnData['messages'] = '图像来源类型错误：%s' % originalImageIndex
        return returnData
    # 从数据库中读取
    dbm = request.__dbManager__
    # 检查是否存在
    mayExists = await getTargetImageByIdAndSource(dbm, imageId, originalImageIndex, 'colorizedModel', model,
                                                   models.ColorizedImage)
    if len(mayExists) > 0:  # 保证只会存在一个
        returnData['messages'] = '使用已经创建的彩色化图片'
        returnData['colorizedModel'] = model
        returnData['imageId'] = mayExists[0].imageId
        returnData['status'] = 0
        returnData['cached'] = True
        # 检查是否有关联的 postID
        returnData['postId'] = await get_postId(dbm, mayExists[0].imageId)
        return returnData
    # 获取图片源的位置
    originalImgFile = getImageFilePath(originalImageIndex, imageid=imageId)  # 原始图片的类型
    originalImgObj = None
    if originalImageIndex == ImageSource.Upload:
        originalImgObj = await dbm.query(models.UploadedImage, imageId=imageId)
    elif originalImageIndex == ImageSource.Styled:
        originalImgObj = await dbm.query(models.StyledImage, imageId=imageId)
    else:
        originalImgObj = await dbm.query(models.ColorizedImage, imageId=imageId)
    # 检查是否存在原文件
    if not os.path.exists(originalImgFile) or not originalImgObj:
        returnData['messages'] = '指定的图片ID对应的文件或记录不存在：%s' % imageId
        return returnData
    # 风格
    ext = imageId[imageId.rfind('.'):]
    colorizedImageId = next_id() + ext
    colorizedImageFile = getImageFilePath(ImageSource.Colorized, colorizedImageId)
    res = methods.colorizer(originalImgFile, colorizedImageFile, imageModelEnum=model_code)
    if not res:
        returnData['messages'] = '没有生成指定的彩色化图片：%s' %  colorizedImageFile
        return returnData
    # 存入数据库
    await dbm.insert(
        models.ColorizedImage,
        imageId=colorizedImageId,
        originalImageId=imageId,
        colorizedModel=model,
        username=username,
        imageSourceIndex=originalImageIndex.value
    )
    returnData['messages'] = '成功彩色化图像'
    returnData['colorizedModel'] = model
    returnData['imageId'] = colorizedImageId
    returnData['status'] = 0
    return returnData


# @routes.get('/api/v1/getImage', name='get_image')  # imageSource={imageSource}&imageId={imageId}
async def get_imageById(request, imageId, imageSource=-1):
    dbm = request.__dbManager__
    if imageSource == -1:
        # 查询所有的可能
        for imgenum in (ImageSource.Upload, ImageSource.Styled, ImageSource.Colorized):
            obj = await getImageFileInDB(dbm, imgenum, imageId)
            if len(obj) == 1:
                return web.FileResponse(path=getImageFilePath(imgSource=imgenum,imageid=imageId))
        return 404

    # 指定了位置
    try:
        srcEnum = ImageSource(int(imageSource))
    except ValueError:
        return 404
    obj = await getImageFileInDB(dbm, srcEnum, imageId)
    if len(obj):
        return web.FileResponse(path=getImageFilePath(imgSource=srcEnum,imageid=imageId))
    else:
        return 404

async def get_ImageItem(request, imageId, imageSourceIndex):
    """
    获取存储在数据库中的图像队对象
    :param request:
    :param imageId: 图像ID
    :param imageSourceIndex: 图像的来源
    :return:
    """
    imageSrcEnum = ImageSource(int(imageSourceIndex))
    dbm = request.__dbManager__
    res = await getImageFileInDB(dbm, imageSrcEnum, imageId)
    if len(res) == 1:
        return res[0]
    else:
        return 404

async def get_uploadRequest(request):
    if not request.__user__:
        return '<p>请您先登录<p><br><a href="/signin">登录</a>'
    else:
        return {
            '__template__': 'upload.html',
            'username': request.__user__.username
        }


async def basic_api_get_userBasedModel(request, sourceIndex):
    """
    为用户提供有针对性的模型信息
    :param request: 请求信息
    :param sourceIndex: 图像来源（仅支持1和2）
    :return:
    """
    sourceIndex = int(sourceIndex)
    models = avaiableModels.get(sourceIndex, None)
    if not models:
        raise ValueError('无效的参数：sourceIndex=%d, 目前经支持1和2。' % sourceIndex)
    return {'models': models}


async def basic_api_get_onBrowserModels(request, sourceIndex):
    """
    获取支持浏览器版本的模型
    :param request:
    :param sourceIndex: 图像来源（仅支持1和2）
    :return:
    """