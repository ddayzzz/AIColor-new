
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
