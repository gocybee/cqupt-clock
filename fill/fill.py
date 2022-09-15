import json
import logging
import os

from requests import request

geocoding_api = 'https://api.map.baidu.com/geocoding/v3/'
reverse_geocoding_api = 'https://api.map.baidu.com/reverse_geocoding/v3/'

GET_LOCATION_ERR = RuntimeError('参数 "location" 没有填写')
GET_AK_ERR = RuntimeError('没有找到 ak 环境变量')
GET_LNG_AND_LAT_ERR = RuntimeError('获取经纬度信息失败')
GET_AREA_CODE_ERR = RuntimeError('获取行政区划代码失败')

logger = logging.getLogger()


class Fill:
    def __init__(self, location):
        self.location = location  # 初始化详细地址
        if self.location is None or self.location == "":
            raise GET_LOCATION_ERR

        self.ak = os.getenv("BAIDU_MAP_API_KEY")  # 初始化百度地图api key
        if self.ak is None or self.ak == "":
            raise GET_AK_ERR

        self.lng, self.lat = self.__get_lng_and_lat()  # 根据详细地址获取经纬度
        self.area_code = self.__get_area_code()  # 根据经纬度获取行政区划代码

    def __get_lng_and_lat(self):
        res = request(method='GET',
                      url=f'{geocoding_api}'
                          f'?address{self.location}'
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

    # 初始化居住地风险等级数据
    def __init_risk_level_data(self):
        return 1

    # 初始化地级市本土疫情数据
    def __init_prefecture_data(self):
        return 1

    # 获取目前居住地风险等级
    def get_risk_level(self):

        return ""

    # 获取7天内所在地级市是否有本土疫情发生
    def get_prefecture_history(self):

        return ""

    # 获取目前居住地是否为风险区或临时管控区域
    def get_is_risk(self):
        return ""
