import browser_cookie3


def get(name):
    cj = browser_cookie3.chrome('./selenium/Default/Network/Cookies', 'ids.cqupt.edu.cn', './selenium/Local State')
    return cj.__dict__.get('_cookies')['ids.cqupt.edu.cn']['/authserver'][name]


# if __name__ == "__main__":
#     print(get('CASTGC'))
