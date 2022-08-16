import datetime
import http.cookiejar
import os.path

import browser_cookie3


def get(name):
    cj = browser_cookie3.chrome(
        cookie_file='./clock/cookies/Default/Cookies',
        domain_name='ids.cqupt.edu.cn',
    )
    return cj.__dict__.get('_cookies')['ids.cqupt.edu.cn']['/authserver'][name]

# if __name__ == "__main__":
#     print(check('CASTGC'))
