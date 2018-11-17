## 登录过程
1. 输入的用户名去掉首尾的留白。
2. 加盐处理：`用户名`+`:`+`密码`。构成新的字符串(由40位十六进制字符构成)。
3. 转换新的字符串为SHA1
4. 发送POST请求：
- 路径：/api/v1/authenticate
- 数据：JSON：`username:<用户名>, passwd:<加盐处理的SHA1>`
5. POST 返回：Response 返回的是设置cookie的响应。cookie的信息
- 会话名称：aicolor_session
- 值：`<用户名>-<超时时间>(自1970年1月1日的秒数）-<40位的十六进制字符串>`
- 超时时间：1天后
## 注销
1. 首先需要登录
2. 发送GET 请求：`/signout`
3. 响应的Cookie：
- 会话名称：aicolor_session
- 值：-deleted-
- maxage：0
## 注册
1. 需要的信息：
- 用户名：英文，非空，不超过50
- 密码：至少六位，不超过50
2. 加盐处理：`用户名`+`:`+`密码`。构成新的字符串(40位十六进制)。
3. 发送 POST
- JSON 数据：`username:<用户名>,passwd_hash:<加盐的字符串>`
3. 创建成功后会自动设置 cookie