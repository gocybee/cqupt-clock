import requests
import json
import datetime
import random
import const
from login import login
import cookie


class DailyClock:

    def __init__(self, **kargs):
        """
        kargs:
            castgc: CASTGC cookie
            name: 你的姓名
            stu_id: 你的学号
        """
        self.cookies = const.Cookies.copy()
        self.cookies['CASTGC'] = cookie.get('CASTGC')
        self.cookies['JSESSIONID'] = cookie.get('JSESSIONID')
        self.cookies['route'] = cookie.get('route')
        self.username = kargs['username']
        self.password = kargs['password']
        self.headers = const.Headers.copy()
        self.role_id = -1
        self.name = kargs['name']
        self.stu_id = kargs['stu_id']
        # 今天的数据是否同步
        self.sync = True
        self.__prepare()
        self.__refresh_WEU()

    def __prepare(self):
        """
        准备 _WEU, MOD_AUTH_CAS
        """
        login(self.username, self.password)
        print(self.cookies.get('CASTGC'))
        resp = requests.get(
            url=const.GET_STU_ID,
            headers=self.headers,
            cookies={'CASTGC': self.cookies.get('CASTGC')}
        )
        if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
            raise BaseException('获取中间 cookie 失败')
        self.cookies['_WEU'] = resp.cookies['_WEU']
        # 第三次重定向会设置 MOD_AUTH_CAS
        self.cookies['MOD_AUTH_CAS'] = resp.history[2].cookies['MOD_AUTH_CAS']
        self.role_id = json.loads(resp.text)['HEADER']['dropMenu'][0]['id']
        resp.close()
        del resp

    def __refresh_WEU(self):
        """
        刷新 _WEU
        """
        refresh_weu = const.REFRESH_WEU_ + self.role_id + '.do'
        resp = requests.get(
            url=refresh_weu,
            headers=self.headers,
            cookies=self.cookies,
        )
        if resp.status_code != 200 or json.loads(resp.text)['success'] != True:
            raise BaseException('更新 _WEU 失败')
        self.cookies['_WEU'] = resp.cookies['_WEU']
        resp.close()
        del resp

    def clock_history(self, today=False, sfdk=None, pageSize=None, pageNum=None):
        __data = {}
        if today:
            __data['RQ'] = datetime.datetime.now().strftime('%Y-%m-%d')
        if sfdk is not None:
            __data['SFDK'] = sfdk
        if pageSize is not None:
            __data['pageSize'] = pageSize
        if pageNum is not None:
            __data['pageNumber'] = pageNum

        resp = requests.post(
            url=const.QUERY_LIST,
            data=__data,
            headers=self.headers,
            cookies=self.cookies,
        )
        if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
            raise BaseException('查询打卡历史失败')
        return json.loads(resp.text)

    def check_today(self):
        """
        检查今天是否打卡
        """
        mess = self.clock_history(today=True)
        rows = mess['datas']['T_XSJKDK_XSTBXX_QUERY']['rows']
        if len(rows) == 0:  # 今天的数据还没有同步
            self.sync = False
            return False
        self.sync = True
        return rows[0]['SFDK'] == '是'

    def __random_titude(self, ratio):
        """
        给经纬度加点噪音
        """
        return round((random.random() * 0.0005) * random.choice((-1, 1)) + ratio, 6)

    def __random_time(self):
        """
        搞点随机的时间，请确保已经过凌晨三点打卡程序才可以启动，不然可能会打错卡
        """
        now = datetime.datetime.now()
        now += datetime.timedelta(hours=random.choice((-2, -1, 0, 1, 2)))  # [-2, 2]
        now += datetime.timedelta(minutes=random.choice((1, -1)) * random.choice(range(60)))
        now += datetime.timedelta(seconds=random.choice((1, -1)) * random.choice(range(60)))
        if now.weekday() != datetime.datetime.now().weekday():
            return self.__random_time()
        return now

    # def get_stu_info(self):
    #     """
    #     获取学生的姓名和学号
    #     """
    #     resp = requests.get(url=const.GET_STU_TYRZM, cookies=self.cookies, headers=self.headers)
    #     if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
    #         print(resp.text)
    #         raise BaseException('获取统一认证码失败')
    #     tyrzm = resp.text
    #     resp.close()
    #     resp = requests.post(url=const.GET_STU_INFO, data={
    #         "pageSize": 1,
    #         "pageNumber": 1,
    #         "SFRZH": tyrzm,
    #     }, cookies=self.cookies, headers=self.headers)
    #     if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
    #         raise BaseException('获取学生信息失败')
    #     mess = json.loads(resp.text)['datas']['V_SSJBXXZB_QUERY']['rows'][0]
    #     return mess['XM'], mess['XH']  # 姓名，学号

    def get_wid(self) -> str:
        """
        获取今天的 WID 字段
        """
        mess = self.clock_history(today=True)
        rows = mess['datas']['T_XSJKDK_XSTBXX_QUERY']['rows']
        if len(rows) == 0:
            self.sync = False
            return ''
        self.sync = True
        return rows[0]['WID']

    def clock(
            self,
            mqjzd="重庆市,重庆市,南岸区",
            jzdxxdz="重庆邮电大学 宁静6",
            tzrysfyc="无同住人员",
            longitude=106.602482,  # 经度 (重庆)
            latitude=29.537199,  # 纬度 (重庆)
            force=False
    ):
        print(f'正在{"准备" if not force else "强制"}给 {self.name} {self.stu_id} 自动打卡...')
        if self.check_today() and (not force):  # 已经打卡了就不打了
            print('今天已经打卡了')
            return
        if not self.sync:
            print('今天数据还未同步，暂时打不了卡')
            return
        __data = {
            'XH': f"{self.stu_id}",  # 学号
            "XM": f"{self.name}",  # 姓名
            "MQJZD": f"{mqjzd}",
            "JZDXXDZ": f"{jzdxxdz}",
            "JZDYQFXDJ": "低风险",
            "SFYZGFXDQLJS": "无",
            "SFJCZGFXDQLJSRY": "无",
            "TWSFZC": "是",
            "SFYGRZZ": "无",
            "TZRYSFYC": f"{tzrysfyc}",
            "YKMYS": "绿色",
            "QTSM": "无",
            "DKSJ": self.__random_time().strftime("%Y-%m-%d %H:%M:%S"),
            "RQ": self.__random_time().strftime("%Y-%m-%d"),
            "SFYC": "否",
            "SFDK": "是",
            "WID": self.get_wid(),
            'SFTS': "是",  # 是否同省份
            'SFTQX': "是",  # 是否同区县
            'LONGITUDE': f'{self.__random_titude(longitude)}',  # 经度 (重庆)
            "LATITUDE": f'{self.__random_titude(latitude)}',  # 纬度 (重庆)
        }
        resp = requests.post(
            url=const.SUBMIT_FORM,
            headers=self.headers,
            cookies=self.cookies,
            data=__data
        )
        if resp.status_code == 200 and json.loads(resp.text)['code'] == '0':
            print(f'打卡成功，当前时间 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'打卡时间：{__data["DKSJ"]}，打卡经纬度 {__data["LONGITUDE"]} : {__data["LATITUDE"]}')
        else:
            print(f'打卡失败，当前时间 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}，返回 {resp.text}')
        resp.close()
        del resp
        return


if __name__ == '__main__':
    for arg in const.ARGS:
        daily = DailyClock(**arg)
        daily.clock('''force=True''')
