import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText

smtp_server = os.getenv("SMTP_SERVER")
if smtp_server is None or smtp_server == "":
    smtp_server = "smtp.qq.com"

account = os.getenv("EMAIL_ACCOUNT")
password = os.getenv("EMAIL_PASSWORD")


# 检验是否开启邮件服务
def check():
    if (account is not None or account != "") and (password is not None or password != ""):
        return True
    return False


def do(msg):
    """
     subject:打卡失败 body: err
     subject:打卡成功 body: 芜湖~~~~~~~~
    """
    message = MIMEText(msg, 'plain', 'utf-8')  # 邮件正文
    # (plain表示mail_body的内容直接显示，也可以用text，则mail_body的内容在正文中以文本的形式显示，需要下载）
    message['From'] = account  # 邮件上显示的发件人
    message['To'] = account  # 邮件上显示的收件人
    message['Subject'] = Header("打卡助手菌来咯", 'utf-8')  # 邮件主题

    smtp = smtplib.SMTP()  # 创建一个连接
    smtp.connect(smtp_server)  # 连接发送邮件的服务器
    smtp.login(account, password)  # 登录服务器
    smtp.sendmail(account, account, message.as_string())  # 填入邮件的相关信息并发送
    smtp.quit()
