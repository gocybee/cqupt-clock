import smtplib
import os

from email.header import Header
from email.mime.text import MIMEText

env_dist = os.environ

my_email = env_dist.get("EMAIL")
my_password = env_dist.get("EMAIL_PWD")


def notice(msg):
    email_smtp_server = "smtp.qq.com"
    """
     subject:打卡失败 body: err
     subject:打卡成功 body: 芜湖~~~~~~~~
    """
    # 发送的邮件正文
    email_msg = MIMEText(msg.body, "plain", "utf-8")
    email_msg["subject"] = Header(msg.subject, "utf-8")
    smtp = smtplib.SMTP_SSL(email_smtp_server, 465)
    # 配置发送邮件的用户名和密码
    smtp.login(my_email, my_password)
    # 配置发送邮件、接受邮件和邮件内容
    smtp.sendmail(my_email, my_email, email_msg.as_string())
