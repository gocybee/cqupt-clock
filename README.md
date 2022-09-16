# CQUPT-CLOCK

[![build](https://img.shields.io/badge/build-1.6.0-brightgreen)](https://github.com/StellarisW/StellarisW)[![image](https://img.shields.io/docker/image-size/stellarisw/cqupt-clock)](https://hub.docker.com/repository/docker/stellarisw/cqupt-clock)[![build](https://img.shields.io/badge/flask-v2.2.2-%230e7fc0)](https://github.com/pallets/flask)[![build](https://img.shields.io/badge/pytorch-v1.12.1-%23f37f40)](https://github.com/pytorch/pytorch)

> 本项目是 **CQUPT 企业微信学生健康打卡** 的一个自动化打卡脚本，可以一定程度上节约**身体健康的同学**申报的时间。
>
> 打卡逻辑主要是通过自动登录获取教务在线的cookie，然后进行企业微信的授权进行打卡。
>
> 登录验证码的识别主要使用 **pytorch** 设计了一个 **3层-CNN 卷积神经网络** 来预测验证码，
>
> 数据集通过模拟教务在线的验证码来自动生成，识别率可以达到 90%。

## 📢 事前声明

1. 本脚本仅供 **学习交流** 使用，请勿过分依赖，时刻注意 **所在地区的风险等级** 及 **自身健康状况**，如有特殊情况，请立即停止该脚本并申报实际情况！
2. 本脚本仅供 **低风险地区** 及 **身体健康状况良好** 的学生使用，如果身体有不适，请立即报告给辅导员
3. 若使用本脚本导致的一切后果，如 **隐瞒自身健康状况**，**误报** 等，本项目概不负责。
4. 请勿将本仓库的任何内容用于**商业**或**非法**目的，否则后果自负。

## 📑 前置条件

1. 需要有一台自己的服务器，最好是 **linux**
2. 需要会部署 **docker**

## ✨ 亮点

- 随机打卡位置

  根据所填经纬度增加**干扰量**
  
- 随机打卡时间

  可以设置一个固定的时间，打卡的时间会在这个时间点进行**抖动**

- 打卡邮件提醒

  每天打卡成功或失败后，会发送**邮件通知**当天的打卡情况

- 智能检测居住地疫情风险情况

  是不是每天打卡这个事情已经够麻烦了，还要查看近期的疫情情况？

  本项目切身体会到了这种感受，根据用户所填详细居住地址，

  **自动检测**用户居住地的**新冠肺炎疫情风险等级**，**新增新冠病毒感染人员情况**

  开发出 **自动填充** 关于 **疫情相关** 的打卡信息的功能


- 验证码识别

  采用 **深度学习** 技术，训练出了验证码识别模型，识别度高达 90%

- 自动检验是否开启验证码

  因为教务在线有时候开验证码，有时候不开，所以加了这个功能

## 🎨 功能说明

### 邮件提醒功能

本项目的邮箱通知功能需要配置 **邮件服务** 的 **SMTP 授权码**

具体以 **QQ邮箱** 为例：

1. 登入QQ邮箱主页

2. 点击 **设置**

    ![image-20220905090116521](https://typora.stellaris.wang/image-20220905090116521.png)

3. 点击 **账户**

    ![image-20220905090153852](https://typora.stellaris.wang/image-20220905090153852.png)

4. 开启 **SMTP 服务** 并生成 **邮箱授权码**

    ![image-20220905090827968](https://typora.stellaris.wang/image-20220905090827968.png)

### 自动填充功能

本项目的自动填充功能需要申请 **百度地图** 的 **API Key**

申请流程如下：

1. 登录 [百度地图开放平台](https://lbsyun.baidu.com/)

2. 点击 **控制台**

    ![image-20220916175514853](https://typora.stellaris.wang/image-20220916175514853.png)

3. 点击 **成为开发者**

    ![image-20220916175611069](https://typora.stellaris.wang/image-20220916175611069.png)

4. 填写所需信息

    开发者信息中的产品用途随便写个100字即可, 不用等待审核会直接通过

5. 申请 API Key

    依次点击 `应用管理` -> `我的应用` -> `创建应用`

    ![image-20220916175948315](https://typora.stellaris.wang/image-20220916175948315.png)

6. 填写应用信息

    ![image-20220916180447643](https://typora.stellaris.wang/image-20220916180447643.png)

7.  复制 **AK**

    进入 `我的应用`，点击复制按钮即可

    ![image-20220916180627167](https://typora.stellaris.wang/image-20220916180627167.png)


## ✈ 部署

本项目通过 **docker** 进行部署，有两种形式，分别为 **服务端** 形式和  **服务端**+**客户端** 形式，对外暴露端口默认为 `:8089`

### 服务端

服务端提供两个接口，分别是 **打卡接口** 和 **验证码识别接口**。

使用这种形式部署需要每天 **手动** 向 **打卡接口** 发送携带用户信息和打卡信息的请求（当然也可以自己写个发送请求的 CRON），然后服务端会自动调用 **验证码识别接口** 来登录，并进行自动打卡。

#### 部署方式1 (推荐)

执行以下命令：

```sh
docker pull stellarisw/cqupt-clock
```

```sh
docker run -it \
--name cqupt-clock \
-d \
--restart=always \
-p 8089:8089 \
-e CLOCK_PORT=8089 \
-e EMAIL_ACCOUNT="" \
-e EMAIL_PASSWORD="" \
-e SMTP_SERVER="" \
stellarisw/cqupt-clock
```

环境变量说明：

- **CLOCK_PORT**：服务端暴露的端口，更改的话需要与上面的 -p 参数进行同步
- **EMAIL_ACCOUNT**：邮箱账号 (可选)
- **EMAIL_PASSWORD**：邮箱授权码 (可选)
- **SMTP_SERVER**：邮箱服务器 (可选, 默认为 QQ邮箱)

#### 部署方式2

执行以下命令

```sh
git clone https://github.com/gocybee/cqupt-clock.git
```

```sh
docker build -t cqupt-clock ./cqupt-clock
```

```sh
docker run -it \
--name cqupt-clock \
-d \
--restart=always \
-p 8089:8089 \
-e CLOCK_PORT=8089 \
-e EMAIL_ACCOUNT="" \
-e EMAIL_PASSWORD="" \
-e SMTP_SERVER="" \
-v $(pwd)/cqupt-clock:/workspace \
cqupt-clock
```

环境变量说明：

- **CLOCK_PORT**：服务端暴露的端口，更改的话需要与上面的 -p 参数进行同步
- **EMAIL_ACCOUNT**：邮箱账号 (可选)
- **EMAIL_PASSWORD**：邮箱授权码 (可选)
- **SMTP_SERVER**：邮箱服务器 (可选, 默认为 QQ邮箱)

#### API 文档

##### 打卡接口

**POST** **/do**

**BODY** **multipart/form-data**

| 参数名             | 参数值样例                | 是否必填    | 描述                                                         |
| ------------------ | ------------------------- | ----------- | ------------------------------------------------------------ |
| name               | xxx                       | 是          | 姓名                                                         |
| stu_id             | 202121xxxx                | 是          | 学号                                                         |
| username           | 16xxxxx                   | 是          | 统一认证码                                                   |
| password           | xxx                       | 是          | 密码                                                         |
| is_today           | true                      | 是          | 是否给今天打卡,选项:"True","False"                           |
| clock_time         | 2022-09-04 17:50:36       | 否          | 给指定日期打卡,格式:"%Y-%m-%d %H:%M:%S"(只有当"is_today"选项为"false"时该选项才填写) |
| is_force           | false                     | 是          | 是否强制打卡(会覆盖之前的打卡记录), 选项:"True","False"      |
| latitude           | 29.536702                 | 是/自动填充 | 纬度                                                         |
| longitude          | 106.611035                | 是/自动填充 | 经度                                                         |
| district           | 重庆市,重庆市,南岸区      | 是          | 地区(根据企业微信里面的表单填写对应的地区)                   |
| location           | 重庆邮电大学 xx苑x舍xxx号 | 是          | 具体地点 (这里一定要具体到楼栋,否则无法判断该楼栋是否是中高风险区 |
| risk_level         | 低风险                    | 是/自动填充 | 目前居住地新冠肺炎疫情风险等级, 选项:"低风险","中风险","高风险","其他" |
| risk_history       | 无                        | 是          | 7天内是否有中高风险地区旅居史, 选项:"无","有"                |
| contact_history    | 无                        | 是          | 7天内否是接触中高风险地区旅居史人员, 选项:"无","有"          |
| prefecture_history | 否                        | 是/自动填充 | 7天内所在地级市是否有本土疫情发生, 选项:"否","是"            |
| is_risk            | 否                        | 是/自动填充 | 目前居住地是否为风险区或临时管控区域, 选项:"否","是"         |
| is_normal_temp     | 是                        | 是          | 今日体温是否正常, 选项:"是","否"                             |
| has_symptom        | 否                        | 是          | 今日是否有与新冠病毒感染有关的症状, 选项:"否","是"           |
| roommates          | 无                        | 是          | 同住人员信息, 选项: "是","无","无同住人员"                   |
| code_color         | 绿色                      | 是          | 渝康码颜色, 选项:"绿色","黄色","红色","其他"                 |

**RESPONSE**

| 字段名  | 字段值样例 | 描述     |
|------|-------|--------|
| code | 200   | 状态码    |
| msg  | 打卡成功  | 消息     |
| ok   | true  | 请求是否成功 |

#### 验证码接口

**GET** **/captcha?timestamp=&session_id=&route=**

**Query**

| 参数名        | 参数值样例                            | 描述                               |
|------------|----------------------------------|----------------------------------|
| timestamp  | 1660383478                       | 教务在线 captcha 请求地址中的 timestamp 参数 |
| session_id | 4EF0AD5BD16FB3ED25VB34A420B510AD | cookie 中的 JSESSIONID             |
| route      | 8e57f1d63642a2d968c01cdaeb9aab9b | cookie 中的 route                  |

**RESPONSE**

| 字段名  | 字段值样例   | 描述     |
|------|---------|--------|
| code | 200     | 状态码    |
| msg  | 获取验证码成功 | 消息     |
| ok   | true    | 请求是否成功 |
| data | s2de    | 验证码    |

#### 其他

如果需要更改打卡配置，则需要执行命令

```sh
docker stop cqupt-clock
```

```sh
docker rm cqupt-clock
```

```sh
docker run -it \
...
```

在第三个命令中，更改相应的配置即可

### 服务端+客户端

使用这种形式部署，可以实现全自动化打卡 (每天根据设定的时间点打卡)，需要配置用户信息和打卡信息配置文件，在项目`cron/info.json`目录下，形式为 **json**，根据[打卡接口文档](#打卡接口)
配置相应的参数值即可，同时还需要配置打卡的时间点和打卡时间抖动范围

```json
{
  "name": "",
  "stu_id": "",
  "username": "",
  "password": "",
  "is_today": "",
  "clock_time": "",
  "is_force": "",
  "latitude": "",
  "longitude": "",
  "district": "",
  "location": "",
  "risk_level": "",
  "risk_history": "",
  "contact_history": "",
  "prefecture_history": "",
  "is_risk": "",
  "is_normal_temp": "",
  "has_symptom": "",
  "roommates": "",
  "code_color": ""
}
```

#### 部署方式一 (推荐)

执行以下命令：

```sh
docker pull stellarisw/cqupt-clock
```

```sh
docker run -it \
--name cqupt-clock \
-d \
--restart=always \
-e ENABLE_CRON="true" \
-e CRON_HOUR=12 \
-e CRON_JITTER=3600 \
-e EMAIL_ACCOUNT="" \
-e EMAIL_PASSWORD="" \
-e SMTP_SERVER="" \
-v $(pwd)/cqupt-clock/cron/info.json:/workspace/cron/info.json \
stellarisw/cqupt-clock
```

环境变量说明：

- **ENABLE_CRON**：开启客户端
- **CRON_HOUR**：设置打卡时间点 (参数范围: 0-23, 默认为12)
- **CRON_JITTER**：设置打卡时间抖动范围 (参数单位: 秒, 默认为3600)
- **EMAIL_ACCOUNT**：邮箱账号 (可选)
- **EMAIL_PASSWORD**：邮箱授权码 (可选)
- **SMTP_SERVER**：邮箱服务器 (可选, 默认为 QQ邮箱)
- **-v .../info.sjon:/workspace/cron/info.json**：填写 **info.json** 文件位置，只需更改":"左边的参数即可

#### 部署方式二

执行以下命令：

```sh
git clone https://github.com/gocybee/cqupt-clock.git
```

```sh
docker build -t cqupt-clock ./cqupt-clock
```

```sh
docker run -it \
--name cqupt-clock \
-d \
--restart=always \
-e ENABLE_CRON="true" \
-e CRON_HOUR=12 \
-e CRON_JITTER=3600 \
-e EMAIL_ACCOUNT="" \
-e EMAIL_PASSWORD="" \
-e SMTP_SERVER="" \
-v $(pwd)/cqupt-clock:/workspace \
cqupt-clock
```

环境变量说明：

- **ENABLE_CRON**：开启客户端
- **CRON_HOUR**：设置打卡时间点 (参数范围: 0-23, 默认为12)
- **CRON_JITTER**：设置打卡时间抖动范围 (参数单位: 秒, 默认为3600)
- **EMAIL_ACCOUNT**：邮箱账号 (可选)
- **EMAIL_PASSWORD**：邮箱授权码 (可选)
- **SMTP_SERVER**：邮箱服务器 (可选, 默认为 QQ邮箱)

#### 其他

如果需要更改打卡信息，直接修改 `info.json` 文件即可

如果需要更改打卡配置，则需要执行命令

```sh
docker stop cqupt-clock
```

```sh
docker rm cqupt-clock
```

```sh
docker run -it \
...
```

在第三个命令中，更改相应的配置即可

## 📝 后序

如果打卡过程中有什么不懂的地方，或者出了什么bug，欢迎提 **issue**

最后如果觉得这个项目用起来好的话，**star** 支持一下

## 📌 TODO

- [x] 自动填写表单-7天内所在地级市是否有本土疫情发生
- [x] 自动填写表单-目前居住地是否为风险区或临时管控区域
- [ ] 自动填写表单-渝康码颜色
