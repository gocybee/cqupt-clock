import hashlib
import json
import logging
import os
import time

from requests import request
from fill.address.match import match_address

geocoding_api = 'https://api.map.baidu.com/geocoding/v3/'
reverse_geocoding_api = 'https://api.map.baidu.com/reverse_geocoding/v3/'
risk_level_api = 'http://bmfw.www.gov.cn/bjww/interface/interfaceJson'
prefecture_history_api = 'https://api.inews.qq.com/newsqa/v1/query/pubished/daily/list?&limit=7'

GET_LOCATION_ERR = RuntimeError('参数没有填写')
GET_AK_ERR = RuntimeError('没有找到 ak 环境变量')
GET_LNG_AND_LAT_ERR = RuntimeError('获取经纬度信息失败')
GET_AREA_CODE_ERR = RuntimeError('获取行政区划代码失败')
GET_RISK_LEVEL_DATA_ERR = RuntimeError('获取疫情风险等级失败')
GET_Prefecture_History_ERR = RuntimeError('分析七天内是否有疫情失败')
GET_Query_Prefecture_History_API_ERR = RuntimeError('请求七天内是否有疫情API失败')

logger = logging.getLogger()


class Fill:
    def __init__(self, ak, location, detail_location):
        self.ak = ak  # 初始化百度地图api key

        self.location = location  # 初始化详细地址
        if self.location is None or self.location == "":
            raise GET_LOCATION_ERR

        self.detail_location = detail_location
        if self.detail_location is None or self.detail_location == "":
            raise GET_LOCATION_ERR

        self.lng, self.lat = self.__get_lng_and_lat()  # 根据详细地址获取经纬度
        self.area_code = self.__get_area_code()  # 根据经纬度获取行政区划代码
        self.__init_risk_level_data()  # 初始化居住地风险等级数据
        self.__query_risk_level_data()  # 判断居住地是否在风险地区名单里面
        self.__query_prefecture_history()  # 判断七天内是否有疫情 0|1

    def __get_lng_and_lat(self):
        res = request(method='GET',
                      url=f'{geocoding_api}'
                          f'?address={self.location}'
                          f'&output=json'
                          f'&ak={self.ak}')
        j = json.loads(res.text)
        if res.status_code != 200 or j['status'] != 0:
            raise GET_LNG_AND_LAT_ERR

        return j['result']['location']['lng'], j['result']['location']['lat']

    def __get_area_code(self):
        res = request(method='GET',
                      url=f'{reverse_geocoding_api}'
                          f'?ak={self.ak}'
                          f'&output=json'
                          f'&coordtype=bd09ll'
                          f'&location={self.lat},{self.lng}')
        j = json.loads(res.text)
        if res.status_code != 200 or j['status'] != 0:
            raise GET_AREA_CODE_ERR
        return j['result']['addressComponent']['adcode']

    def __init_risk_level_data(self):
        timestamp = int(time.time())
        raw_signature = 'fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA'
        raw_another_signature = '23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA'

        x_wif_nouce = 'QkjjtiLM2dCratiA'
        x_wif_paasid = 'smt-application'

        h1 = hashlib.sha256()
        h1.update(f'{timestamp}{raw_signature}{timestamp}'.encode('utf-8'))
        x_wif_signature = h1.hexdigest().upper()

        x_wif_timestamp = str(timestamp)

        headers = {
            'Content-Type': "application/json",
            'x-wif-nonce': x_wif_nouce,
            'x-wif-paasid': x_wif_paasid,
            'x-wif-signature': x_wif_signature,
            'x-wif-timestamp': x_wif_timestamp,
        }

        nonce_header = '123456789abcdefg'

        h2 = hashlib.sha256()
        h2.update(f'{timestamp}{raw_another_signature}{nonce_header}{timestamp}'.encode('utf-8'))

        data = {
            'area_code': self.area_code,
            'key': '2CA32596474B4077834CCC191D351839',
            'appId': 'NcApplication',
            'paasHeader': 'zdww',
            'timestampHeader': timestamp,
            'nonceHeader': nonce_header,
            'signatureHeader': h2.hexdigest().upper()
        }

        res = request(method='POST',

                      url=risk_level_api,
                      headers=headers,
                      data=json.dumps(data))

        if res.status_code != 200:
            raise GET_RISK_LEVEL_DATA_ERR

        j = json.loads(res.text)
        self.risk_level_data = j['data']

    def __query_risk_level_data(self):
        self.risk_level = self.risk_level_data['level_code']

        if not self.risk_level_data['list']:
            risk_data_list = self.risk_level_data['list']

            for risk_data in risk_data_list:
                if match_address(self.detail_location, risk_data['community_name']):
                    self.risk_level = risk_data['level']
                    break

    def __query_prefecture_history(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.88 Safari/537.36',
            'Accept-Language': 'zh-CN, zh',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8, '
                      'application/signed-exchange;v=b3;q=0.9',
        }

        rq = request.Request(headers=headers,
                             url=f'{prefecture_history_api}'
                                 f'&adCode={self.area_code}',
                             )
        resp = request.urlopen(rq)
        j = json.loads(resp.read())
        data = j['data']

        for i in data:
            if i['confirm_add'] != 0:
                self.prefecture_history = 1
        self.prefecture_history = 0

    # TODO: 抓包疫情数据
    # 初始化地级市本土疫情数据
    def __init_prefecture_data(self):
        return 1

    # 获取经纬度信息
    def get_lng_and_lat(self):
        return self.lng, self.lat

    # 获取目前居住地风险等级
    def get_risk_level(self):
        return self.risk_level

    # 获取7天内所在地级市是否有本土疫情发生
    def get_prefecture_history(self):

        return self.prefecture_history

        # 获取目前居住地是否为风险区或临时管控区域

    def get_is_risk(self):
        if self.risk_level == 2 or self.risk_level == 3:
            return True
        return False
