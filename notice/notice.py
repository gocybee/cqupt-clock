import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText

email_smtp_server = "smtp.qq.com"

env_dict = os.environ

account = env_dict.get("EMAIL_ACCOUNT")
password = env_dict.get("EMAIL_PASSWORD")


def check():
    if account is not None and password is not None:
        return True
    return False


def do(msg):
    """
     subject:打卡失败 body: err
     subject:打卡成功 body: 芜湖~~~~~~~~
    """
    message = MIMEText(msg.body, 'plain', 'utf-8')  # 邮件正文
    # (plain表示mail_body的内容直接显示，也可以用text，则mail_body的内容在正文中以文本的形式显示，需要下载）
    message['From'] = account  # 邮件上显示的发件人
    message['To'] = account  # 邮件上显示的收件人
    message['Subject'] = Header(msg.subject, 'utf-8')  # 邮件主题

    smtp = smtplib.SMTP()  # 创建一个连接
    smtp.connect(email_smtp_server)  # 连接发送邮件的服务器
    smtp.login(account, password)  # 登录服务器
    smtp.sendmail(account, account, message.as_string())  # 填入邮件的相关信息并发送
    smtp.quit()
