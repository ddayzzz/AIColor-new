# 基本的API使用
用户上传、风格化和彩色化的图像郡保存在服务端上。如果用户对具有相同的图像ID进行**相同的**风格化或彩色化，那么服务端返回保存在服务器上的内容的对应JSON或者响应：在例子中`使用已经创建的彩色化图片`就表明是使用的保存的内容而非再次生成的冗余副本（通常初次生成会很慢）。
### 图像ID
- 形式：<标识>.<文件的扩展名>
- 例子：`15380544603201b39e720af6a40aea323ddc633072f4b000.jpg`
### 上传图片（需要扩展名）
- 方法：POST
- 路径：/api/v1/upload
- 返回值：JSON：
- 是否使用 Cookie：是
```json
{"status": 200, "data": {"imagesIds": ["<图像Id1>", "<图像Id2>"]}}
```
返回值|意义
-|-
imagesIds|列表，元素是存储在服务端的图像ID。可以以此进行后续的操作
### 风格化图片
- 方法：GET
- 路径：/api/v1/getStyled/originalImageId
- 查询参数：
- 是否使用 Cookie：是

参数|意义|是否必须|**例子**
-|-|-|-
originalImageId|源图像的ID|是|xxx.jpg
styledModel|风格化采用的画风模型|是|Starrynight等
originalImageIndex|源图像的位置|是|0：用户的上传，1：风格化保存的目录，2：彩色化保存的目录
示例用法：`/api/v1/getStyled?originalImageId=<图像ID>&styledModel=Starrynight&originalImageIndex=0`
- 返回值：JSON：
```json
{"status": 0, "data": {"originalImageId": "<图像ID>", "originalImageIndex": "0", "styledModel": "Starrynight", "messages": "使用已经创建的风格化图片", "imageId": "<图像ID>"}}
```
返回值|意义
-|-
imageId|存储在服务端的已经按照要求风格化图像ID。可以以此进行后续的操作
### 彩色化图片
- 方法：GET
- 路径：/api/v1/getColorized
- 查询参数：
- 是否使用 Cookie：是

参数|意义|是否必须|例子
-|-|-|-
originalImageId|源图像的ID|是|xxx.jpg
colorizedModel|彩色化采用的画风模型|是|字符串。Normal：默认的上色模型;ImageNet：使用 ImageNet 预训练的模型；Animation：动漫彩色化（仅JPEG）
originalImageIndex|源图像的位置|是|0：用户的上传，1：风格化保存的目录，2：彩色化保存的目录
示例用法：`/api/v1/getColorized?originalImageId=<图像ID>&colorizedModel=t1&originalImageIndex=0`
- 返回值：JSON：
```json
{"status": 0, "data": {"originalImageId": "<图像ID>", "originalImageIndex": "0", "colorizedModel": "t1", "messages": "使用已经创建的彩色化图片", "imageId": "<图像ID>"}}
```
返回值|意义
-|-
imageId|存储在服务端的已经按照要求彩色化图像ID。可以以此进行后续的操作
### 得到保存在服务端的图片
- 方法：GET
- 路径：/api/v1/getImage
- 查询参数：
是否使用 Cookie：否

参数|意义|是否必须|例子
-|-|-|-
imageSource|源图像的位置|否（匹配imagid的图像）|0：用户的上传，1：风格化保存的目录，2：彩色化保存的目录
imgid|<图像ID>|是|xxx.png

示例用法：`/api/v1/getImage?imageSource=0&imageId=<图像ID>`
- 返回值：图像的响应或者404
# 社交方面
### 获取用户上传的所有图片
- 方法：GET
- 路径：/api/v1/getImages
- 是否使用 Cookie：否

参数|意义|是否必须|例子
-|-|-|-
username|用户名|是|test123
- 返回值：JSON：
```JSON
{"status": 0, "data": {"upload": [{"uploadImageId": "15399676514052dc00f88e48a48f7a81f021332c7b633000.jpeg", "username": "user1", "created_time": 1539967651.45584}, {"uploadImageId": "1539967651421bf8b997ec6964dbf9214466f9f00ed68000.jpeg", "username": "user1", "created_time": 1539967651.45885}], "colorized": [], "styled": []}}
```
`data` 中有三个类型的用户相关的图片数据，数据是一个可为空的列表。每一个条目是对应的ID、上传的用户名和对应创建的日期（自1970-01-01的秒数）。按照创建时间的降序排列。
### 获取评论信息
- 方法：GET
- 路径：/api/v1/getComments
- 查询参数：
- 是否使用 Cookie：否

参数|意义|是否必须|例子
-|-|-|-
imageId|图像ID（上传、彩色化和风格化）|是|id.extname
- 返回值：
```json
{"status": 0, "data": {"total":1, "comments": [{"imageId": "1539967651421bf8b997ec6964dbf9214466f9f00ed68000.jpeg", "username": "user1", "created_time": 1540002736.53212, "comment": "Naie"}]}}
```
返回值名|意义
-|-
total|评论总数
comments|评论的条目字典。
imageId|某一条评论的关联图片id
username|某一条评论的关联用户名
comment|评论的内容，长度不超过200
created_time|评论时间，精确到毫秒
### 插入评论
- 方法：POST
- 路径：/api/v1/insertComment
- 是否使用 Cookie：是
- 查询参数：

参数|意义|是否必须|例子
-|-|-|-
imageId|图像ID（上传、彩色化和风格化）|是|id.extname
comment|评论，不超过200个字符的字符串|是|Naive
- 返回值：JSON
```JSON
{"status": 0}
```
### 获取点赞详情
- 方法：GET
- 路径：/api/v1/getLikes
- 是否使用 Cookie：否
- 查询参数：

参数|意义|是否必须|例子
-|-|-|-
imageId|图像ID（上传、彩色化和风格化）|是|id.extname
- 返回值：JSON
```JSON
{"status": 0, "data": {"total": 1, "liked": [{"imageId": "15399676514052dc00f88e48a48f7a81f021332c7b633000.jpeg", "username": "user1", "liked": 1}]}}
```
API 返回的是指定图片ID的点赞信息，`liked`都是值是数值化的布尔值，在这里获取的是点赞的信息，所以每个条目都是的`liked`值都是1。
返回值名|意义
-|-
total|点赞人数
liked|点赞的条目字典。
imageId|某一点赞用户关联的图片id，对应于GET的`imageId`参数。
username|某一点赞的用户名
liked|1
### 反转点赞状态
- 方法：POST
- 路径：/api/v1/flipLikeStatus
- 是否使用 Cookie：是
- 查询参数：

参数|意义|是否必须|例子
-|-|-|-
imageId|图像ID（上传、彩色化和风格化）|是|id.extname
- 返回值：JSON
- 与用户登录状态有关，请设置 Cookie
```json
{"status": 0, "data": {"flipped": true}}
```
`flipped`表明图片点赞状态反转后的值，表明用户是否对`imageId`进行了点赞。
### 获取所有在服务器上最新的图片
- 方法：GET
- 路径：/api/v1/getImageTimeline
- 是否使用 Cookie：否
  
参数|意义|是否必须|例子
-|-|-|-
username|用户名|否|test123
**注意**： 如果指定了用户名，将返回特定用户名在服务器上最新的图片的序列。否则返回的是所有用户的最新图片序列。
- 返回值：JSON。`data.sorted_desc`列表元素按照`created_time`的降序排列。

```json
{"status": 0, "data": {"sorted_desc": [{"imageId": "1540301018223fb62b643ab6e428d990aa600510ed8ae000.jpeg", "username": "test", "created_time": 1540301018.24596, "srcIndex": 0}, {"imageId": "1540300996895e5b1be4af5b74cb5a47bea7d08335fda000.jpeg", "username": "test2", "created_time": 1540300996.93871, "srcIndex": 0}, {"imageId": "1540217241444e934157b2f554e048b499ed6a95afc69000.jpeg", "username": "test", "created_time": 1540217241.48471, "srcIndex": 0}, {"imageId": "1540216911854a7fa21a571c04cde899c26dea9008053000.jpeg", "username": "test", "created_time": 1540216911.87362, "srcIndex": 0}, {"imageId": "154021232522136dca2d49b1f49d79edcc3401712e4f4000.jpg", "originalImageId": "1540212167922ab44a022bbb14737a6d84ae56daf80c6000.jpg", "styledModel": "Cubist", "username": "test", "imageSourceIndex": 0, "created_time": 1540212356.53859, "srcIndex": 1}, {"imageId": "15402122331138c5987ca2d194ee1a0b88d7f81b93f84000.jpg", "originalImageId": "154021217046836192e10dbe44f359956d10e43e857af000.jpg", "styledModel": "Starrynight", "username": "test", "imageSourceIndex": 0, "created_time": 1540212243.82504, "srcIndex": 1}, {"imageId": "15402121920139d414f6e82964c85997e4b90c445a01e000.jpg", "originalImageId": "154021217046836192e10dbe44f359956d10e43e857af000.jpg", "colorizedModel": "t1", "username": "test", "imageSourceIndex": 0, "created_time": 1540212197.60519, "srcIndex": 2}, {"imageId": "154021217046836192e10dbe44f359956d10e43e857af000.jpg", "username": "test", "created_time": 1540212170.46882, "srcIndex": 0}, {"imageId": "1540212167922ab44a022bbb14737a6d84ae56daf80c6000.jpg", "username": "test", "created_time": 1540212167.92342, "srcIndex": 0}, {"imageId": "1540212162322b46339eeaf0a4358ab5b5e9f936c10e1000.jpg", "username": "test", "created_time": 1540212162.32377, "srcIndex": 0}, {"imageId": "1540210899408103cc8600c30442c8c889c795de6f9b5000.jpeg", "username": "test", "created_time": 1540210899.43988, "srcIndex": 0}, {"imageId": "1540210894921e7eebdc8d13a40cbad3de3b8275cf8e8000.jpeg", "username": "test", "created_time": 1540210894.96566, "srcIndex": 0}, {"imageId": "1540210556993b743fae8a2b848f59d99a7623f5a6fad000.jpeg", "username": "test", "created_time": 1540210557.0182, "srcIndex": 0}]}}
```
返回值举例：
```json
{"imageId": "1540217241444e934157b2f554e048b499ed6a95afc69000.jpeg", "username": "test", "created_time": 1540217241.48471, "srcIndex": 0}
```
键|意义
-|-
imageId|图像ID
username|用户名
created_time|图像创建的日期
srcIndex|图像的来源。取值0，1和2分别表示来源于上传、风格化和彩色化。
likes--不再包含|字典，`total`表示赞的人数。`liked`表示用户关于此图片的点赞情况，值是以类似`{"imageId": "1540217241444e934157b2f554e048b499ed6a95afc69000.jpeg", "username": "test", "liked": 1}`为元素的列表。
### 获取可用的模型
- 方法：GET
- 路径：/api/v1/getModels
- 是否使用 Cookie：否
  
参数|意义|是否必须|例子
-|-|-|-
sourceIndex|基于图片来源的模型代码|是|目前仅支持：1：基于风格化的模型列表；2：基于彩色化的模型列表

返回值举例：
```json
{
"status": 0,
"data": {
"models": [
{
"name": "Candy",
"desc": "Candy 画派",
"image": "/static/images/styled/candy-style.jpg"
},
{
"name": "Cubist",
"desc": "立体主义",
"image": "/static/images/styled/cubist-style.jpg"
},
....
{
"name": "Edtaonisl",
"desc": "Edtaonisl 画派",
"image": "/static/images/styled/edtaonisl-style.jpg"
}
]
}
}
```
键|意义
-|-
name|模型名
desc|模型描述
image|模型的介绍图片
# 例子
```
/api/v1/getStyled?originalImageId=15380544603201b39e720af6a40aea323ddc633072f4b000.jpg&styledModel=Starrynight&originalImageIndex=0
```
```
/api/v1/getColorized?originalImageId=15380544603201b39e720af6a40aea323ddc633072f4b000.jpg&colorizedModel=t1&originalImageIndex=0
```
```
/api/v1/getImage?imageSource=0&imageId=15380544603201b39e720af6a40aea323ddc633072f4b000.jpg
```