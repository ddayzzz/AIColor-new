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