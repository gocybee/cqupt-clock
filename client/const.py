import datetime

## 注意：请确保已经过凌晨三点打卡程序才可以启动，不然可能会打错卡

#####  CASTGC Cookies 列表，填入需要自动打卡的同学的 CASTGC Cookie

# 获取 CASTGC Cookie 的办法：
# 打开 https://ids.cqupt.edu.cn/authserver/login
# 然后选择 “7天内免登录”，登录你的账户，最后在跳转到的网站那查看 cookies，
# 就会有一个叫 CASTGC 的 cookie
# 如果打开上面的网站直接跳转到登录好的页面的话，那你之前可能选过 7天内免登录，
# 可以删除所有 Cookie 后重新获取一个新的 CASTGC

USERNAME = ''
PASSWORD = ''

ARGS = [
    {
        'name': '',  # 填写你的姓名
        'stu_id': '',  # 填写你的学号
        'username': '',  # 填写你的统一认证码
        'password': '',  # 填写你的密码
    }
]
#####

# 伪造请求头
Headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'com.tencent.wework',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; M2007J17C Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 wxwork/4.0.0 ColorScheme/Dark MicroMessenger/7.0.1 NetType/4G Language/zh Lang/zh',
    'Referer': 'http://ehall.cqupt.edu.cn/publicapp/sys/cyxsjkdkmobile/*default/index.html'
}

# 伪造 cookies
Cookies = {
    # 三个比较重要的 cookie
    'CASTGC': '',
    '_WEU': '',
    'MOD_AUTH_CAS': '',
    # 不重要的
    '.ASPXAUTH1': '9861B91FC0EC40660E17267C20AE9B8ABC75FDD77F61EC63D504D2D06E486C43CBBDDEB0140F01CA125F9149E5A12FA157BADE827DEE1F36F9A7234EE139E421FA1C3C6D5582E36AD8B5D9505CC80BB04378FA2BA97D69E1485BD95653E47A9BEA909BB03466AE39889063E35BEC7D38C368A3607A0BA3E230C9D525644CCA350255603848C3C4BC5B0AC6BF158953E51D0FF11992BEE3D48504A8913E4F73B4BE9D8073ABD12E311EB0EB40D1921A5FFAD1E2A17672E4D02E5C4478A6B2017B',
    'JSESSIONID': 'bBfMPifgXVKYxpL3oSIARqtnZ0FYJ4ftsIzCxMu5NkCybmeKCMrV?-64737101',
    'route': '25636182ad6de114514f3ee1a23d8ec8',
    'client_vpn_ticket': 'qUQXOxv22:694a32-ab88-840e8a1av9b2',
}

HOST = 'http://ehall.cqupt.edu.cn/publicapp'

# POST 打卡接口
# 需要有 _WEU，MOD_AUTH_CAS
SUBMIT_FORM = HOST + '/sys/cyxsjkdk/modules/yddjk/T_XSJKDK_XSTBXX_SAVE.do'

# POST 七天打卡历史
# 需要有 _WEU，MOD_AUTH_CAS
# Query 中加 pageSize，pageNumber，SFDK，RQ 来限制数量
QUERY_LIST = HOST + '/sys/cyxsjkdk/modules/yddjk/T_XSJKDK_XSTBXX_QUERY.do'


class QUERY_LIMIT:
    @classmethod
    def DAY_OF(clz, day, append=None):
        if isinstance(day, datetime.datetime):
            day = day.strftime('%Y-%m-%d')
        if append is not None:
            append['RQ'] = day
            return append
        return {'RQ': day}

    @classmethod
    def SFDK(clz, boolean, append=None):
        if append is not None:
            append['SFDK'] = '是' if boolean else '否'
            return append
        return {'SFDK': '是' if boolean else '否'}

    @classmethod
    def PAGE_LIMIT(size, num, append=None):
        if append is not None:
            append['pageSize'] = size
            append['pageNumber'] = num
            return append
        return {'pageSize': size, 'pageNumber': num}


# GET 获取学生的 ID
# 需要 MOD_AUTH_CAS 或者 CASTGC
# 如果发送时用 CASTGC 则会返回一个 MOD_AUTH_CAS 和 _WEU
GET_STU_ID = HOST + '/sys/funauthapp/api/getAppConfig/cyxsjkdkmobile-6578524306216816.do?GNFW=MOBILE'

# GET 刷新_WEU 后面需要加上学生ID.do
REFRESH_WEU_ = HOST + '/sys/funauthapp/api/changeAppRole/cyxsjkdk/'

# POST 获取学生信息
# 需要 pageSize, pageNumber, SFRZH
GET_STU_INFO = HOST + '/publicapp/sys/cyxsjkdk/modules/yddjk/V_SSJBXXZB_QUERY.do'

# GET 获取学生统一认证码
GET_STU_TYRZM = HOST + '/publicapp/sys/cyxsjkdk/getUserId.do'
