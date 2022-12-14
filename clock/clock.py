import datetime
import json
import logging
import random

import requests

from clock import const as const
from clock import cookie
from clock.login import login

logger = logging.getLogger()


class DailyClock:

    def __init__(self, args=dict):
        # 初始化个人信息
        class StudentInfo:
            def __init__(self, name, stu_id, username, password):
                self.name = name
                self.id = stu_id
                self.username = username
                self.password = password

        logger.info('初始化个人信息...')
        self.studentInfo = StudentInfo(
            name=args['name'],
            stu_id=args['stu_id'],
            username=args['username'],
            password=args['password'],
        )

        # 初始化打卡信息
        class ClockDetails:
            def __init__(self, district, location, risk_level, risk_history,
                         contact_history, prefecture_history, is_risk, is_normal_temp,
                         has_symptom, roommates, code_color, longitude, latitude):
                self.district = district
                self.location = location
                self.risk_level = risk_level
                self.risk_history = risk_history
                self.contact_history = contact_history
                self.prefecture_history = prefecture_history
                self.is_risk = is_risk
                self.is_normal_temp = is_normal_temp
                self.has_symptom = has_symptom
                self.roommates = roommates
                self.code_color = code_color
                self.longitude = longitude
                self.latitude = latitude

        logger.info('初始化打卡信息...')
        self.clockDetails = ClockDetails(
            district=args['district'],
            location=args['location'],
            risk_level=args['risk_level'],
            risk_history=args['risk_history'],
            contact_history=args['contact_history'],
            prefecture_history=args['prefecture_history'],
            is_risk=args['is_risk'],
            is_normal_temp=args['is_normal_temp'],
            has_symptom=args['has_symptom'],
            roommates=args['roommates'],
            code_color=args['code_color'],
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
        logger.info(r'获取 "CASTGC" cookie...')
        logger.info('登录中...')
        try:
            login(self.studentInfo.username, self.studentInfo.password)
        except BaseException:
            logger.error('登录失败')
            raise const.LOGIN_ERR

        # 获取中间cookie
        logger.info('获取中间cookie...')
        s = requests.session()
        s.cookies.set_cookie(cookie=cookie.get('CASTGC'))

        # 根据'CASTGC'cookie获取'_WEU','MOD_AUTH_CAS'等cookie
        try:
            resp = s.request(method='GET',
                             url=const.GET_STU_ID,
                             headers=self.headers)
            if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
                logger.error('获取中间cookie失败')
                raise const.GET_MIDDLE_COOKIE_ERR
        except BaseException:
            logger.error('获取中间cookie失败')
            raise const.GET_MIDDLE_COOKIE_ERR

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
        logger.info(r'刷新 "_WEU" cookie...')
        refresh_weu = const.REFRESH_WEU_ + self.roleId + '.do'
        resp = requests.get(
            url=refresh_weu,
            headers=self.headers,
            cookies=self.cookies,
        )
        if resp.status_code != 200 or json.loads(resp.text)['success'] != True:
            logger.info(r'刷新 "_WEU" cookie...')
            raise const.UPDATE_WEU_ERR
        self.cookies['_WEU'] = resp.cookies['_WEU']
        resp.close()
        del resp

    def clock_history_on(self, date=None, sfdk=None, page_size=None, page_num=None):
        """
        查询打卡历史信息
        date: 字符串(例如 2022-08-10 )，会覆盖 today，锁定某一天的历史
        sfdk: 是/否/None，限制是否打卡的记录
        pageSize: 限制打卡记录页大小
        pageNum: 限制打卡记录页数目
        """
        __data = {}
        if date is not None:
            __data['RQ'] = date
        if sfdk is not None:
            __data['SFDK'] = sfdk
        if page_size is not None:
            __data['pageSize'] = page_size
        if page_num is not None:
            __data['pageNumber'] = page_num

        resp = requests.post(
            url=const.QUERY_LIST,
            data=__data,
            headers=self.headers,
            cookies=self.cookies,
        )
        if resp.status_code != 200 or resp.headers['Content-Type'].__contains__('text/html'):
            raise const.GET_CLOCK_HISTORY_ERR
        return json.loads(resp.text)

    def check_date(self, date):
        """
        检查指定日期是否打卡
        """
        mess = self.clock_history_on(date=date)
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
        搞点随机的时间
        """
        now = pivot
        # now += datetime.timedelta(hours=random.choice((-2, -1, 0, 1, 2)))  # [-2, 2]
        now += datetime.timedelta(minutes=random.choice(range(5)))
        now += datetime.timedelta(seconds=random.choice(range(60)))
        # if now.weekday() != datetime.datetime.now().weekday():
        #     return self.__random_time()
        return now

    def get_wid_on(self, date) -> str:
        """
        获取今天的 WID 字段
        """
        mess = self.clock_history_on(date=date)
        rows = mess['datas']['T_XSJKDK_XSTBXX_QUERY']['rows']
        if len(rows) == 0:
            self.sync = False
            return ''
        self.sync = True
        return rows[0]['WID']

    def clock_on(
            self,
            clock_time: datetime.datetime,
            force=False
    ):
        clock_date = clock_time.strftime('%Y-%m-%d')
        wid = self.get_wid_on(date=clock_date)
        logger.info(f'正在{"准备" if not force else "强制"}给 {self.studentInfo.name} {self.studentInfo.id} 自动打卡...')
        if self.check_date(date=clock_date) and (not force):  # 已经打卡了就不打了
            logger.error('已经打过卡了')
            raise const.ALREADY_CLOCK_ERR
        if not self.sync:
            logger.error('打卡数据未同步')
            raise const.DATA_NOT_SYNC_ERR
        __data = {
            'XH': f"{self.studentInfo.id}",  # 学号
            "XM": f"{self.studentInfo.name}",  # 姓名
            "MQJZD": f"{self.clockDetails.district}",  # 目前居住地
            "JZDXXDZ": f"{self.clockDetails.location}",  # 居住地详细地址
            "JZDYQFXDJ": f"{self.clockDetails.risk_level}",  # 居住地风险等级
            "SFYZGFXDQLJS": f"{self.clockDetails.risk_history}",  # 有无中高风险旅居史
            "SFJCZGFXDQLJSRY": f"{self.clockDetails.contact_history}",  # 有无接触中高风险地区旅居史人员
            "SZDJSSFYYQFS": f"{self.clockDetails.prefecture_history}",  # 七天内居住地是否有疫情发生
            "JZDSFFXQHLSGKQY": f"{self.clockDetails.is_risk}",  # 居住地是否风险区或临时管控区域
            "TWSFZC": f"{self.clockDetails.is_normal_temp}",  # 体温是否正常
            "SFYGRZZ": f"{self.clockDetails.has_symptom}",  # 是否有症状
            "TZRYSFYC": f"{self.clockDetails.roommates}",  # 同住人员情况
            "YKMYS": f"{self.clockDetails.code_color}",  # 渝康码颜色
            "QTSM": "无",  # 其他说明
            "DKSJ": self.__random_time(clock_time).strftime("%Y-%m-%d %H:%M:%S"),  # 打卡具体时间
            "RQ": clock_date,  # 打卡日期
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
            logger.info(f'打卡成功，当前时间 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(f'打卡时间：{__data["DKSJ"]}，打卡经纬度 {__data["LONGITUDE"]} : {__data["LATITUDE"]}')
        else:
            logger.error(f'打卡失败，当前时间 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}，返回 {resp.text}')
        resp.close()
        del resp
        return
