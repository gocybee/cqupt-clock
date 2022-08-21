import json
import logging
import os
import time

import requests
from selenium import webdriver

from clock import const as const


class By(object):
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"


logger = logging.getLogger()

LOGIN_URL = 'https://ids.cqupt.edu.cn/authserver/login'


def login(username, password):
    option = webdriver.ChromeOptions()
    current_dir_path = os.getcwd()
    option.add_argument(f'user-data-dir={current_dir_path}/clock/cookies')  # 设置用户数据存储位置
    option.add_argument('-no-sandbox')  # 让chrome在root权限下跑
    option.add_argument('-disable-dev-shm-usage')
    option.add_argument('-headless')  # 不用打开图形界面
    option.add_argument('-disable-cookie-encryption')  # 取消cookie加密

    browser = webdriver.Chrome(chrome_options=option)

    # browser.maximize_window()
    # 打开页面
    browser.get(LOGIN_URL)
    # 隐式等待10秒(等待加载完页面再执行后续操作)
    browser.implicitly_wait(10)

    time.sleep(3)

    if "personalInfo" in browser.current_url:
        logger.info('使用之前的"CASTGC"cookie')
        browser.close()
        return

    login_count = 0
    while 1:
        login_count = login_count + 1
        logger.info(f'正在尝试第{login_count}次登录')
        # 输入账号和密码
        logger.debug(browser.current_url)
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

        '''
        如果登录成功则跳出循环
        反之重新登录
        这样可以避免识别验证码出错的情况
        '''
        time.sleep(3)
        if "personalInfo" in browser.current_url:
            logger.info('登录成功')
            browser.close()
            return

        '''
        如果登录五次还没有登录成功,则停止登录
        防止账号被冻结
        '''
        if login_count == 5:
            logger.error('登录失败')
            browser.close()
            raise const.LOGIN_ERR
