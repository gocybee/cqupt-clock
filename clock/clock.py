import datetime
import json
import random

import requests

from clock import const as const
from clock import cookie
from clock.login import login


def get():
    print(1)


class DailyClock:

    def __init__(self, args):
        # 初始化个人信息
        class StudentInfo:
            def __init__(self, name, stu_id, username, password):
                self.name = name
                self.id = stu_id
                self.username = username
                self.password = password

        self.studentInfo = StudentInfo(
            name=args['name'],
            stu_id=args['stu_id'],
            username=args['username'],
            password=args['password'],
        )

        # 初始化打卡信息
        class ClockDetails:
            def __init__(self, district, location, roommates, longitude, latitude):
                self.district = district
                self.location = location
                self.roommates = roommates
                self.longitude = longitude
                self.latitude = latitude

        self.clockDetails = ClockDetails(
            district=args['district'],
            location=args['location'],
            roommates=args['roommates'],
            longitude=args['longitude'],
            latitude=args['latitude'],
        )

        self.roleId = str(-1)

        self.headers = const.Headers.copy()
        self.cookies = const.Cookies.copy()

        # 今天的数据是否同步
        self.sync = True
        self.__prepare()
        self.__refresh_WEU()

    def __prepare(self):
        """
        准备 认证cookie
        """

        # 自动登录获取'CASTGC'等cookie
        if not login(self.studentInfo.username, self.studentInfo.password):
            raise RuntimeError('登录失败')

        s = requests.session()
        s.cookies.set_cookie(cookie=cookie.get('CASTGC'))

        # 根据'CASTGC'cookie获取'_WEU','MOD_AUTH_CAS'等cookie
        resp = s.request(method='GET',
                         url=const.GET_STU_ID,
                         headers=self.headers)
        if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
            raise RuntimeError('获取中间 cookie 失败')

        print(self.cookies)
        self.cookies['_WEU'] = resp.cookies['_WEU']
        # 第一次重定向会设置 'MOD_AUTH_CAS'
        self.cookies['MOD_AUTH_CAS'] = resp.history[2].cookies['MOD_AUTH_CAS']
        self.roleId = json.loads(resp.text)['HEADER']['dropMenu'][0]['id']
        # 第二次重定向会设置 'JSESSIONID'和'route'
        self.cookies['JSESSIONID'] = resp.history[1].cookies['JSESSIONID']
        self.cookies['route'] = resp.history[1].cookies['route']
        resp.close()
        del resp

    def __refresh_WEU(self):
        """
        刷新 _WEU
        """
        refresh_weu = const.REFRESH_WEU_ + self.roleId + '.do'
        resp = requests.get(
            url=refresh_weu,
            headers=self.headers,
            cookies=self.cookies,
        )
        if resp.status_code != 200 or json.loads(resp.text)['success'] != True:
            raise RuntimeError('更新 _WEU 失败')
        self.cookies['_WEU'] = resp.cookies['_WEU']
        resp.close()
        del resp

    def clock_history_on(self, rq=None, sfdk=None, pageSize=None, pageNum=None):
        """
        查询打卡历史信息
        rq: 字符串(例如 2022-08-10 )，会覆盖 today，锁定某一天的历史
        sfdk: 是/否/None，限制是否打卡的记录
        pageSize: 限制打卡记录页大小
        pageNum: 限制打卡记录页数目
        """
        __data = {}
        if rq is not None:
            __data['RQ'] = rq
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
            raise RuntimeError('查询打卡历史失败')
        return json.loads(resp.text)

    def check_date(self, rq):
        """
        检查指定日期是否打卡
        """
        mess = self.clock_history_on(rq=rq)
        rows = mess['datas']['T_XSJKDK_XSTBXX_QUERY']['rows']
        if len(rows) == 0:  # rq 的数据还没有同步
            self.sync = False
            return False
        self.sync = True
        return rows[0]['SFDK'] == '是'

    @staticmethod
    def __random_titude(ratio):
        """
        给经纬度加点噪音
        """
        ratio = float(ratio)
        return round((random.random() * 0.0005) * random.choice((-1, 1)) + ratio, 6)

    @staticmethod
    def __random_time(pivot: datetime.datetime):
        """
        搞点随机的时间，请确保已经过凌晨三点打卡程序才可以启动，不然可能会打错卡
        """
        now = pivot
        now += datetime.timedelta(hours=random.choice((-2, -1, 0, 1, 2)))  # [-2, 2]
        now += datetime.timedelta(minutes=random.choice((1, -1)) * random.choice(range(60)))
        now += datetime.timedelta(seconds=random.choice((1, -1)) * random.choice(range(60)))
        # if now.weekday() != datetime.datetime.now().weekday():
        #     return self.__random_time()
        return now

    def get_wid_on(self, rq) -> str:
        """
        获取今天的 WID 字段
        """
        mess = self.clock_history_on(rq=rq)
        rows = mess['datas']['T_XSJKDK_XSTBXX_QUERY']['rows']
        if len(rows) == 0:
            self.sync = False
            return ''
        self.sync = True
        return rows[0]['WID']

    def clock_on(
            self,
            date: datetime.datetime,
            force=False
    ):
        rq = date.strftime('%Y-%m-%d')
        wid = self.get_wid_on(rq=rq)
        print(f'正在{"准备" if not force else "强制"}给 {self.studentInfo.name} {self.studentInfo.id} 自动打卡...')
        if self.check_date(rq=rq) and (not force):  # 已经打卡了就不打了
            print(f'{rq} 已经打卡了')
            return
        if not self.sync:
            print(f'{rq} 数据还未同步，暂时打不了卡')
            return
        __data = {
            'XH': f"{self.studentInfo.id}",  # 学号
            "XM": f"{self.studentInfo.name}",  # 姓名
            "MQJZD": f"{self.clockDetails.district}",  # 目前居住地
            "JZDXXDZ": f"{self.clockDetails.location}",  # 居住地详细地址
            "JZDYQFXDJ": "低风险",  # 居住地风险等级
            "SFYZGFXDQLJS": "无",  # 有无中高风险旅居史
            "SFJCZGFXDQLJSRY": "无",  # 有无接触中高风险地区旅居史人员
            "TWSFZC": "是",  # 体温是否正常
            "SFYGRZZ": "无",  # 是否有症状
            "TZRYSFYC": f"{self.clockDetails.roommates}",  # 同住人员情况
            "YKMYS": "绿色",  # 渝康码颜色
            "QTSM": "无",  # 其他说明
            "DKSJ": self.__random_time(date).strftime("%Y-%m-%d %H:%M:%S"),  # 打卡具体时间
            "RQ": self.__random_time(date).strftime("%Y-%m-%d"),  # 打卡日期
            "SFYC": "否",
            "SFDK": "是",
            "WID": wid,
            'SFTS': "是",  # 是否同省份
            'SFTQX': "是",  # 是否同区县
            'LONGITUDE': f'{self.__random_titude(self.clockDetails.longitude)}',  # 经度
            "LATITUDE": f'{self.__random_titude(self.clockDetails.latitude)}',  # 纬度
        }

        # 发送打卡请求
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
