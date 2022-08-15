import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText

email_smtp_server = "smtp.qq.com"

env_dist = os.environ

account = env_dist.get("EMAIL_ACCOUNT")
password = env_dist.get("EMAIL_PASSWORD")


def notice(msg):
    """
     subject:打卡失败 body: err
     subject:打卡成功 body: 芜湖~~~~~~~~
    """
    # 发送的邮件正文
    email_msg = MIMEText(msg.body, "plain", "utf-8")
    email_msg["subject"] = Header(msg.subject, "utf-8")
    smtp = smtplib.SMTP_SSL(email_smtp_server, 465)
    # 配置发送邮件的用户名和密码
    smtp.login(account, password)
    # 配置发送邮件、接受邮件和邮件内容
    smtp.sendmail(account, account, email_msg.as_string())
