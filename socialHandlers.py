import re
import hashlib
from aiohttp import web
import json
import time
import logging

import models
from bases import ImageSource, next_id, avaiableModels
from bases import get_loggined_username_or_denied, just_get_username
from bases import getImageFileInDB




async def _getImages(imgSrc, dbm, username=None):
    """
    查询某个用户上传、风格化和彩色化的图片对象，结果是按照创建时间的降序排列
    :param imgSrc: 图片源编号
    :param username: 用户名，为空表示获取所有的图片
    :param dbm: 数据库操作对象
    :return:
    """
    sql_where = None
    args = None
    if username:
        sql_where = 'username=?'
        args = [username]
    if imgSrc == ImageSource.Upload:
        return await dbm.queryAll(model_type=models.UploadedImage, sql_where=sql_where, args=args, orderBy='created_time desc')
    elif imgSrc == ImageSource.Colorized:
        return await dbm.queryAll(model_type=models.ColorizedImage, sql_where=sql_where, args=args, orderBy='created_time desc')
    elif imgSrc == ImageSource.Styled:
        return await dbm.queryAll(model_type=models.StyledImage, sql_where=sql_where, args=args, orderBy='created_time desc')


async def social_zone(request, username=None):
    """
    获取用户空间网页
    :param request:
    :return:
    """
    Loginedusername = just_get_username(request)
    if not username:
        if Loginedusername:
            username = Loginedusername
        else:
            return 403
    return {'__template__': 'zone2.html', 'username': Loginedusername, 'targetUsername': username}  # 注意我这里的名称是主键


async def social_flow(request):
    username = just_get_username(request)
    return {'__template__': 'flow.html', 'username': username}


async def social_api_get_getAllImages(request, username):
    dbm = request.__dbManager__
    return {
        'upload': await _getImages(ImageSource.Upload, username=username, dbm=dbm),
        'colorized': await _getImages(ImageSource.Colorized, username=username, dbm=dbm),
        'styled': await _getImages(ImageSource.Styled, username=username, dbm=dbm)
    }


async def social_api_get_getComments_inPost(request, postId):
    """
    获取关于帖子的评论树
    :param request: 请求
    :param postId: 帖子的 ID
    :return:
    """
    dbm = request.__dbManager__
    ret_data ={
        'status': 1,
        'postId': postId,
        'comments': None,
        'message': None
    }
    # 查询指定的帖子
    result = await dbm.query(models.Post, postId=postId)
    if not result:
        ret_data['message'] = '没有找到指定的帖子：' + postId
        return ret_data
    # 获取评论信息，按照时间的升序排列。
    comments = await dbm.queryAll(models.Comment, sql_where='postId=?', args=(postId, ), orderBy='created_time desc')
    ret_data['comments'] = comments
    return ret_data


async def social_api_post_insertComment(request, postId, comment, replyUsername=None):
    """
    插入一个帖子中的评论
    :param request:
    :param postId: 帖子 ID
    :param comment: 评论的内容（不超过200字符）
    :param replyUsername: 回复的用户名
    :return:
    """
    username = get_loggined_username_or_denied(request)
    dbm = request.__dbManager__
    # 检查评论是否存在
    postObj = await dbm.query(models.Post, postId=postId)
    if not postObj:
        return {'status': 1}
    # 新建评论
    aComment = models.Comment(commentId=next_id(), username=username, comment=comment, postId=postId,
                              to_username=replyUsername)
    await dbm.insert(aComment)
    return {'status': 0, 'comment': aComment}


async def social_api_get_getLikes_inPost(request, postId, username=None):
    """
    获取帖子的点赞信息
    :param request: 请求
    :param postId: 帖子ID
    :param username: 指定点赞的用户名（可空）
    :return:
    """
    dbm = request.__dbManager__
    # 查询帖子是否存在
    postObj = await dbm.query(models.Post, postId=postId)
    ret = {'total': 0, 'status': 1, 'liked': None}
    if not postObj:
        return ret
    # 查询点赞
    where = 'postId=? and liked=?'
    args = [postId, True]
    if username:
        where = where + ' and username=?'
        args.append(username)
    liked = dbm.queryAll(models.Like, sql_where=where, args=args)
    ret['total'] = len(liked)
    ret['liked'] = liked
    return ret


async def social_api_post_flipLikeStatus(request, postId=None, likeId=None):
    """
    反转点赞的状态。当 likeId 为空时，根据 postId 和 用户 cookie 创建新的已经点赞的信息；likeId 不为空，根据相关的对象反转点赞的信息
    :param request: 请求
    :param postId: 帖子Id
    :param likeId: 点赞的Id
    :return:
    """
    username = get_loggined_username_or_denied(request)
    dbm = request.__dbManager__
    if not likeId:
        # 新建新的信息
        if not postId:
            raise ValueError('请指定 postId')
        likedObj = models.Like(likId=next_id(),
                               username=username,
                               postId=postId,
                               liked=False)
        await dbm.insert(likedObj)
    else:
        # 查询已经存在的(建议加上用户名验证等信息)
        likedObj = await dbm.query(models.Like, likeId=likeId)
    # 反转
    if not likedObj:
        raise ValueError('没有指定的帖子点赞对象')
    likedObj.liked = not likedObj.liked
    # 保存到数据库
    await dbm.update(likedObj)
    return likedObj


async def _get_postId(dbm, imageId):
    res = await dbm.queryAll(models.Post, sql_where='imageId=?', args=(imageId))
    if len(res) > 0:
        return res[0].postId
    else:
        return None

async def _getAllImagesTimeline(dbm, imageSrc, username=None):
    """
    获取某个用户或者所有用户上传的图像，可以指定来源。按照创建时间降序排列
    :param dbm:
    :param imageSrc: 图像的来源
    :param username:
    :return:
    """
    imageSrc = int(imageSrc)
    res = None
    # 获取上传的信息
    if imageSrc == ImageSource.Colorized.value:
        res = await _getImages(ImageSource.Colorized, username=username, dbm=dbm)
    elif imageSrc == ImageSource.Styled.value:
        res = await _getImages(ImageSource.Styled, username=username, dbm=dbm)
    elif imageSrc == ImageSource.Upload.value:
        res = await _getImages(ImageSource.Upload, username=username, dbm=dbm)
    # 加入其他的属性
    postedList = [(await _get_postId(dbm, item.imageId)) for item in res]  # https://stackoverflow.com/questions/40746213/how-to-use-await-in-a-python-lambda
    for i in range(len(res)):
        res[i]['postId'] = postedList[i]  # 不要用 update None值无法插入
    # 合并信息
    return {'sorted_desc': res}


async def social_api_get_getImageTimeline(request, imageSrc, username=None):
    # 获取降序排列的图片
    loginusername = just_get_username(request)
    if not username:
        if not loginusername:
            # 既没指定查看的用户 有没登录
            return 'redirect:/'
        else:
            # 转到对应的用户
            username = loginusername
    return await _getAllImagesTimeline(request.__dbManager__, imageSrc, username)

async def social_api_post_createPost(request, imgId, imgSrcIndex, title):
    """
    创建一个帖子(需要登陆)
    :param request: 请求
    :param imgId: 图像Id
    :param imgSrcIndex: 图像索引
    :param title: 标题
    :return: 返回帖子对象
    """
    # 获取用户 ID
    username = get_loggined_username_or_denied(request)
    # 创建 Post 对象
    postObj = models.Post(title=title,
                          imageId=imgId,
                          imageSourceIndex=imgSrcIndex,
                          username=username)
    # 保存指定的 ORM 对象
    dbm = request.__dbManager__
    await dbm.insert(postObj)
    # 这里有个问题，如果没任何的评论和点赞信息，那么无法床获得对应的帖子。所以添加一个对应的默认点赞信息和评论信息
    postId = postObj.postId
    defaultliked = models.Like(postId=postId,
                               username='default',
                               liked=True)
    defaultComment = models.Comment(postId=postId,
                                    comment="添加第一条评论吧",
                                    username="default",
                                    to_username=None)
    await dbm.insert(defaultComment)
    await dbm.insert(defaultliked)
    # 返回指定的对象
    return {'postInfo': postObj}


async def social_api_get_postTimeLine(request):
    """
    获取帖子的时间线，不是正对某一个用户的请求
    :param request: 请求
    :return: 返回包含点赞信息(已经点赞)的 post 时间线
    """
    dbm = request.__dbManager__
    posts = await dbm.queryAll(models.PostLikeView, orderBy='created_time desc')
    return {'sorted_desc': posts}



async def social_api_getUserLikeStatus(request):
    """
    获取用户在一系列帖子的状态, 需要登录
    :param request:
    :return:
    """
    username = get_loggined_username_or_denied(request)
    dbm = request.__dbManager__
    ret = await dbm.select(models.UserLikeOnPost, sql_where='l.`username`=? and l.`postId`=p.`postId`', args=(username, ), toDict=True)  # 注意多表连接的主键要相同
    return ret


async def social_view_post(request, postId):
    username = just_get_username(request)
    # 查询帖子的存在
    dbm = request.__dbManager__
    postObj = await dbm.query(models.Post, postId=postId)
    if not postObj:
        return 404
    # 查询是否存在指定的照片
    imgIndexEnum = ImageSource(int(postObj.imageSourceIndex))
    imgObj = await getImageFileInDB(dbm, imgSrcEnum=imgIndexEnum, imgid=postObj.imageId)
    if len(imgObj) != 1:
        return 404
    return {'__template__': 'viewPost.html', 'username': username, 'postObj': postObj, 'imageObj': imgObj[0]}


async def social_image_processer(request, imageId, imageSrcIndex):
    """
    对某个图片进行处理，返回页面
    :param request: 请求
    :param imageId: 图像ID
    :param imageSrcIndex: 图像来源的索引
    :return:
    """
    username = get_loggined_username_or_denied(request)  # 必须登录
    return {'__template__': 'processer.html',
            'username': username,
            'imageId': imageId,
            'imageSrcIndex': imageSrcIndex,
            'styledModels': avaiableModels.get(1),
            'coloredModels': avaiableModels.get(2)}




