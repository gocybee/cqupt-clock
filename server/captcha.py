import http.cookiejar
from io import BytesIO

import requests
from PIL import Image
from matplotlib import pyplot as plt

import pytorch.predict as predict

# 设置获取captcha的请求头

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'connection': 'close',
    'host': 'ids.cqupt.edu.cn',
    'referer': 'https://ids.cqupt.edu.cn/authserver/login?service=http%3A%2F%2Fehall.cqupt.edu.cn%2Flogin%3Fservice'
               '%3Dhttp%3A%2F%2Fehall.cqupt.edu.cn%2Fnew%2Findex.html',
    'sec-fetch-mode': 'cors',
    "sec-fetch-site": 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 '
                  'Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}


def get_captcha_img(timestamp, session_id, route):
    s = requests.session()
    s.cookies['route'] = route
    s.cookies['org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE'] = 'zh_CN'
    s.cookies['JSESSIONID'] = session_id
    img_response = s.get(url='https://ids.cqupt.edu.cn/authserver/getCaptcha.htl?' + timestamp,
                         headers=headers)
    img_response.close()
    image = Image.open(BytesIO(img_response.content))
    plt.imshow(image)
    plt.show()
    return image


def get_captcha_answer(img=Image.Image):
    return predict.get(img)
