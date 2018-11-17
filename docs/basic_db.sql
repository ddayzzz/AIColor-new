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