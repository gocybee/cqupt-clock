import datetime
import logging
import os
from distutils.util import strtobool

from flask import Flask, request, jsonify

from captcha import captcha as c
from clock.clock import DailyClock as Clock
from notice import notice

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logfile = './log/log.txt'
if not os.path.exists(logfile):
    if not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))
    file = open(logfile, 'w')
    file.close()

fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

app = Flask('jwzx')


@app.route('/captcha', methods=['get'])
def captcha():
    """
    query:
        "timestamp": "",   填写captcha请求地址中的timestamp参数
        "session_id": "",  填写cookie中的JSESSIONID的value
        "route": "",       填写cookie中的route的value
    """
    req = request.args.to_dict()
    try:
        timestamp = req['timestamp']
        session_id = req['session_id']
        route = req['route']
    except KeyError as err:
        logger.error(f'获取验证码失败,参数{err.args[0]}没有填写')
        res = {
            "code": "401",
            "ok": "false",
            "msg": f'获取验证码失败,参数{err.args[0]}没有填写',
            "data": ""
        }
        return jsonify(res), 401
    # 通过时间戳和session_id获取对应的captcha
    try:
        img = c.get_captcha_img(timestamp, session_id, route)
    except ConnectionError:
        logger.error('获取验证码图片失败')
        res = {
            "code": "500",
            "ok": "false",
            "msg": "获取验证码失败,没有获取到验证码图片",
            "data": ""
        }
        return jsonify(res), 500
    # 获取对应captcha的answer
    answer = c.get_captcha_answer(img)
    logger.info(f'获取到验证码答案:{answer}')
    res = {
        "code": "200",
        "msg": "获取验证码成功",
        "ok": "true",
        "data": answer
    }
    return jsonify(res), 200


@app.route('/do', methods=['post'])
def do():
    """
    form:
        "name": "",               填写你的姓名
        "stu_id": "",             填写你的学号
        "username": "",           填写你的统一认证码
        "password": "",           填写你的密码
        "district": "",           填写你的地区,例如:"重庆市,重庆市,南岸区"
        "location": "",           填写你的具体地点,例如:"重庆邮电大学 宁静6"
        "risk_level": "",         填写目前居住地新冠肺炎疫情风险等级,选项:"低风险","中风险","高风险","其他"
        "risk_history": "",       填写7天内是否有中高风险地区旅居史,选项:"无","有"
        "contact_history: "",     填写7天内否是接触中高风险地区旅居史人员,选项:"无","有"
        "prefecture_history": "", 填写7天内所在地级市是否有本土疫情发生,选项:"否","是"
        "is_risk": "",            填写目前居住地是否为风险区或临时管控区域,选项:"否","是"
        "is_normal_temp: "",      填写今日体温是否正常,选项:"是","否"
        "has_symptom": "",        填写今日是否有与新冠病毒感染有关的症状,选项:"否","是"
        "roommates": "",          填写同住人员是否异常,选项: "是","无","无同住人员"
        "code_color": "",         填写你的渝康码颜色,选项:"绿色","黄色","红色","其他"
        "longitude": "",          填写你的经度,例如: 106.608634
        "latitude": "",           填写你的维度,例如: 29.528421
        "is_force": "",           是否强制打卡(会覆盖之前的打卡记录),选项:"True","False"
        "is_today": "",           是否给今天打卡,选项:"True","False"
        "clock_time" "",          给指定日期打卡,格式:"%Y-%m-%d %H:%M:%S"(只有当"is_today"选项为"false"时该选项才填写)
    """
    req = request.form.to_dict()
    try:
        clock = Clock(args=req)
    except KeyError as err:
        res = {
            "code": "401",
            "msg": f'参数"{err.args[0]}"没有填写',
            "ok": "false"
        }
    except BaseException as err:
        res = {
            "code": "401",
            "msg": f'{err.args[0]}',
            "ok": "false"
        }
    else:
        logger.info('获取cookie成功')
        try:
            if strtobool(req['is_today']):
                clock.clock_on(clock_time=datetime.datetime.now(), force=strtobool(req['is_force']))
            else:
                clock.clock_on(clock_time=datetime.datetime.strptime(req['clock_time'], "%Y-%m-%d %H:%M:%S"),
                               force=strtobool(req['is_force']))
        except KeyError as err:
            res = {
                "code": "401",
                "msg": f'参数"{err.args[0]}"没有填写',
                "ok": "false"
            }
        except BaseException as err:
            res = {
                "code": "401",
                "msg": f'{err.args[0]}',
                "ok": "false"
            }
        else:
            res = {
                "code": "200",
                "msg": "打卡成功",
                "ok": "true"
            }
            if notice.check():
                notice.do(res['msg'])
                return jsonify(res), int(res['code'])

    if notice.check():
        notice.do(res['msg'])
        logger.error('打卡失败')
        return jsonify(res), 401


if __name__ == '__main__':
    port = os.getenv("CLOCK_PORT")
    if port is None or port == "":
        port = 8089
    app.run(host='0.0.0.0', port=port, debug=False)
