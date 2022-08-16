
## 容器部署
```
docker build -t cqupt-clock .
```

```
docker run -it \
-p 8089:8089 \
-d \
--restart=always \
--name cqupt-clock \
-v /www/wwwroot/jwzx.stellaris.wang:/workspace \ # 改一下项目代码文件放的位置
-e EMAIL_ACCOUNT="" \ # 设置邮箱账号
-e EMAIL_PASSWORD="" \ # 设置邮箱授权码
cqupt-clock
```

## API接口文档

### "/do","post","form"

```
"name": "",        填写你的姓名
"stu_id": "",      填写你的学号
"username": "",    填写你的统一认证码
"password": "",    填写你的密码
"district": "",    填写你的地区,例如:"重庆市,重庆市,南岸区"
"location": "",    填写你的具体地点,例如:"重庆邮电大学 宁静6"
"roommates": "",   填写同住人员是否异常,选项: "是","无","无同住人员"
"longitude": "",   填写你的经度,例如: 106.608634
"latitude": "",    填写你的维度,例如: 29.528421
"is_force": "",    是否强制打卡(会覆盖之前的打卡记录),选项:"True","False"
"is_today": "",    是否给今天打卡,选项:"True","False"
"clock_time": "",  给指定日期打卡,格式:"%Y-%m-%d %H:%M:%S"(只有当"is_today"选项为"false"时该选项才填写)
```

### "/captcha","get","query"

```
"timestamp": "",   填写captcha请求地址中的timestamp参数
"session_id": "",  填写cookie中的JSESSIONID的value
"route": "",       填写cookie中的route的value
```