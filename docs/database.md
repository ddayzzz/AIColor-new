# 建立基本的数据库
```sql
use aicolor;

drop table if exists users;
drop table if exists styled_images;
drop table if exists colorized_images;
drop table if exists uploaded_images;

create table users(
username varchar(50),
passwd varchar(50),
created_time real,
primary key(username)
)character set = utf8;

create table uploaded_images(
imageId varchar(80),
username varchar(50),
created_time real,
primary key(imageId)
)character set = utf8;

create table styled_images(
imageId varchar(80),
styledModel varchar(30),
originalImageId varchar(80),
imageSourceIndex smallint,
username varchar(50),
created_time real,
primary key(imageId)

)character set = utf8;

create table colorized_images(
imageId varchar(80),
colorizedModel varchar(10),
originalImageId varchar(80),
username varchar(50),
imageSourceIndex smallint,
created_time real,
primary key(imageId)

)character set = utf8;
```
# 建立用户数据库
```sql
use aicolor;

drop table if exists comments;
drop table if exists likes;
drop table if exists posts;


create table comments(
commentId varchar(80),
created_time real,
comment varchar(200),
postId varchar(80),
username varchar(50),
to_username varchar(50) null,
primary key(commentId)
)character set = utf8;

create table likes(
likeId varchar(80),
username varchar(50),
postId varchar(80),
liked boolean,
primary key(LikeId)
)character set = utf8;

create table posts(
postId varchar(80),
title varchar(100),
imageId varchar(80),
imageSourceIndex smallint,
created_time real,
username varchar(50),
primary key(postId)
)character set = utf8;
```
# 建立视图
```sql

use aicolor;
drop view if exists post_like_view;
drop view if exists post_comment_view;

-- 创建视图: 帖子ID，帖子的其他信息，点赞ID，点赞的信息

create view post_like_view(postId, title, imageId, imageSourceIndex, created_time, username, likedCount) as
select p.postId, p.title, p.imageId, p.imageSourceIndex, p.created_time, p.username, count(p.postId) from posts p, likes l 
where l.postId = p.postId and l.liked = 1
group by p.postId;


-- 创建视图: 帖子ID，帖子的其他信息，评论ID，评论的信息
create view post_comment_view(postId, title, imageId, imageSourceIndex, created_time, username, commentId, commentTime, comment, commentUsername, comment_to_username) as
select p.postId, p.title, p.imageId, p.imageSourceIndex, p.created_time, p.username,l.commentId, l.created_time, l.comment, l.username, l.to_username from posts p, comments l where
l.postId = p.postId;

```