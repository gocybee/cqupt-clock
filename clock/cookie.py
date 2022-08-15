import datetime
import http.cookiejar
import os.path

import browser_cookie3


def get(name):
    cj = browser_cookie3.chrome('./clock/cookies/Default/Cookies',
                                'ids.cqupt.edu.cn',
                                './clock/cookies/Local State')
    return cj.__dict__.get('_cookies')['ids.cqupt.edu.cn']['/authserver'][name]


def check(name):
    # 检查cookie是否存在
    if not os.path.exists('./cookies/Default/Cookies'):
        return False

    cj = browser_cookie3.chrome(
        cookie_file='./cookies/Default/Cookies',
        domain_name='ids.cqupt.edu.cn',
    )

    c = cj.__dict__.get('_cookies')['ids.cqupt.edu.cn']['/authserver'][name]
    # cookie没有过期
    if datetime.datetime.now().timestamp() < c.expires:
        return True
    # cookie过期了
    return False


# if __name__ == "__main__":
#     print(check('CASTGC'))
