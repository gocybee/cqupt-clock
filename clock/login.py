import json
import os
import time

import requests
from selenium import webdriver


class By(object):
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"


LOGIN_URL = 'https://ids.cqupt.edu.cn/authserver/login'


def login(username, password):
    # 设置chrome存储用户数据的位置(cookies)
    chrome_option = webdriver.ChromeOptions()
    current_dir_path = os.getcwd()
    chrome_option.add_argument(f'user-data-dir={current_dir_path}/selenium')

    browser = webdriver.Chrome(chrome_options=chrome_option)

    # browser.maximize_window()
    # 打开页面
    browser.get(LOGIN_URL)
    # 隐式等待10秒(等待加载完页面再执行后续操作)
    browser.implicitly_wait(10)
    login_count = 0
    while 1:
        login_count = login_count + 1
        # 输入账号和密码
        browser.find_element(By.ID, 'username').clear()
        browser.find_element(By.ID, 'username').send_keys(username)
        browser.find_element(By.ID, 'password').clear()
        browser.find_element(By.ID, 'password').send_keys(password)

        # 获取captcha的请求地址
        captcha_url = browser.find_element(By.ID, 'captchaImg').get_attribute('src')
        # 获取captcha的当前时间戳
        timestamp = (captcha_url[(captcha_url.find('?') + 1):])

        # 获取cookie中的'JSESSIONID'和'route'

        session_id = browser.get_cookie('JSESSIONID').get('value')
        route = browser.get_cookie('route').get('value')

        # 获取验证码答案
        res = requests.get(
            'http://localhost:8089/captcha?timestamp=%s&session_id=%s&route=%s' % (timestamp, session_id, route))
        j = json.loads(res.text)

        # 输入验证码
        browser.find_element(By.ID, 'captcha').send_keys(j['data'])

        # 点击按钮"7天内免登录"
        browser.find_element(By.ID, 'rememberMe').click()
        # 点击按钮"登录"
        browser.find_element(By.ID, 'login_submit').click()
        time.sleep(5)

        '''
        如果登录成功则跳出循环
        反之重新登录
        这样可以避免识别验证码出错的情况
        '''
        if "accountsecurity" in browser.current_url:
            return True

        '''
        如果登录五次还没有登录成功,则停止登录
        防止账号被冻结
        '''
        if login_count == 5:
            return False
