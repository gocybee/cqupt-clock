import datetime
import logging
from distutils.util import strtobool

from flask import Flask, request, jsonify

from captcha import captcha as c
from clock.clock import DailyClock as Clock
from notice import notice

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logfile = './log.txt'
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
            "data": "",
            "msg": f'获取验证码失败,参数{err.args[0]}没有填写'
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
            "data": "",
            "msg": "获取验证码失败,没有获取到验证码图片"
        }
        return jsonify(res), 500
    # 获取对应captcha的answer
    answer = c.get_captcha_answer(img)
    logger.info(f'获取到验证码答案:{answer}')
    res = {
        "code": "200",
        "ok": "true",
        "data": answer,
        "msg": "获取验证码成功"
    }
    return jsonify(res), 200


@app.route('/do', methods=['post'])
def do():
    """
    form:
        "name": "",        填写你的姓名
        "stu_id": "",      填写你的学号
        "username": "",    填写你的统一认证码
        "password": "",    填写你的密码
        "district": "",    填写你的地区,例如:"重庆市,重庆市,南岸区"
        "location": "",    填写你的具体地点,例如:"重庆邮电大学 宁静6"
        "roommates": "",   填写同住人员是否异常,选项: "是","无","无同住人员"
        "longitude": "",   填写你的经度,例如: 106.608634
        "latitude": "",    填写你的维度,例如: 29.528421
        "is_force": "",    是否强制打卡(会覆盖之前的打卡记录),选项:"True","False"
        "is_today": "",    是否给今天打卡,选项:"True","False"
        "clock_time" "",   给指定日期打卡,格式:"%Y-%m-%d %H:%M:%S"(只有当"is_today"选项为"false"时该选项才填写)
    """
    req = request.form.to_dict()
    try:
        clock = Clock(args=req)
    except KeyError as err:
        res = {
            "code": "401",
            "ok": "false",
            "msg": f'参数"{err.args[0]}"没有填写'
        }
    except BaseException as err:
        res = {
            "code": "401",
            "ok": "false",
            "msg": f'{err.args[0]}'
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
                "ok": "false",
                "msg": f'参数"{err.args[0]}"没有填写'
            }
        except BaseException as err:
            res = {
                "code": "401",
                "ok": "false",
                "msg": f'{err.args[0]}'
            }
        else:
            res = {
                "code": "200",
                "ok": "true",
                "msg": "打卡成功"
            }
        if notice.check():
            notice.do(res['msg'])
        return jsonify(res), int(res['code'])
    if notice.check():
        notice.do(res['msg'])
    logger.info('打卡成功')
    return jsonify(res), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089, debug=False)
