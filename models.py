# coding=utf-8
__author__ = 'Shu Wang <wangshu214@live.cn>'
__version__ = '0.0.0.1'
__all__ = ['User'
]
from orm import *
import time
from handlers import next_id


class User(Model):

    __table__ = 'users'  # 表的位置
    passwd = StringField(column_type='varchar(50)')
    username = StringField(column_type='varchar(50)', primary_key=True)
    created_time = FloatField(default=time.time)


class UploadedImage(Model):

    __table__ = 'uploaded_images'
    # 主键
    imageId = StringField(column_type='varchar(80)', primary_key=True)
    # 其他的建
    username = StringField(column_type='varchar(50)')
    created_time = FloatField(default=time.time)


class ColorizedImage(Model):

    __table__ = 'colorized_images'
    # 主键
    imageId = StringField(column_type='varchar(80)', primary_key=True)
    # 其他的建
    originalImageId = StringField(column_type='varchar(80)')
    colorizedModel = StringField(column_type='varchar(10)')
    username = StringField(column_type='varchar(50)')
    imageSourceIndex = SmallIntField()
    created_time = FloatField(default=time.time)


class StyledImage(Model):

    __table__ = 'styled_images'
    # 主键
    imageId = StringField(column_type='varchar(80)', primary_key=True)
    # 其他的建
    originalImageId = StringField(column_type='varchar(80)')
    styledModel = StringField(column_type='varchar(30)')
    username = StringField(column_type='varchar(50)')
    imageSourceIndex = SmallIntField()
    created_time = FloatField(default=time.time)


class Comment(Model):

    __table__ = 'comments'
    # 评论ID
    commentId = StringField(column_type='varchar(80)', primary_key=True, default=next_id)
    # 创建日期
    created_time = FloatField(default=time.time)
    # 评论内容
    comment = StringField(column_type='varchar(200)')
    # 关联的 Post
    postId = StringField(column_type='varchar(80)')
    # 评论者
    username = StringField(column_type='varchar(50)')
    # 回复对象(单独的评论表示 None)
    to_username = StringField(column_type='varchar(50)')


class Like(Model):

    __table__ = 'likes'
    # 点赞的ID
    likeId = StringField(column_type='varchar(80)', primary_key=True, default=next_id)
    # 点赞的用户
    username = StringField(column_type='varchar(50)')
    # 点赞的状态，如果之后用户取消了点赞则还是不能计入点赞的总数
    liked = BooleanField(default=lambda : False)
    # 关联的 Post
    postId = StringField(column_type='varchar(80)')


class Post(Model):
    # 帖子列表
    __table__ = 'posts'
    # 帖子ID
    postId = StringField(column_type='varchar(80)', primary_key=True, default=next_id)
    # 标题
    title = StringField(column_type='varchar(100)')
    # 对应的图像ID
    imageId = StringField(column_type='varchar(80)')
    # 图像的来源
    imageSourceIndex = SmallIntField()
    # 创建日期
    created_time = FloatField(default=time.time)
    # 用户名
    username = StringField(column_type='varchar(50)')


class PostLikeView(Model):
    # 帖子-点赞视图
    __table__ = 'post_like_view'
    # 帖子ID
    postId = StringField(column_type='varchar(80)', primary_key=True)
    # 标题
    title = StringField(column_type='varchar(100)')
    # 对应的图像ID
    imageId = StringField(column_type='varchar(80)')
    # 图像的来源
    imageSourceIndex = SmallIntField()
    # 创建日期
    created_time = FloatField()
    # 用户名
    username = StringField(column_type='varchar(50)')
    # 点赞相关
    likedCount = IntegerField()

class UserLikeOnPost(TempModel):
    """
    某一个用户的关于所有帖子的点赞信息
    """

    __tables__ = {'likes': 'l', 'posts': 'p'}
    postId = StringField(column_type='varchar(80)', prefix='p', primary_key=True)
    likeId = StringField(column_type='varchar(80)', prefix='l')
    imageId = StringField(column_type='varchar(80)', prefix='p')
    username = StringField(column_type='varchar(50)', prefix='l')
    likedStatus = BooleanField(prefix='l', name='liked')
