import datetime

from flask import Flask, request, jsonify

from captcha import captcha as c
from clock import const as const
from clock.clock import DailyClock as Clock

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
        res = {
            "code": "401",
            "ok": "false",
            "data": "",
            "msg": f'获取验证码失败,参数{err.args[0]}没有填写'
        }
        return jsonify(res), 401
    # 通过时间戳和session_id获取对应的captcha
    img = c.get_captcha_img(timestamp, session_id, route)
    # 获取对应captcha的answer
    answer = c.get_captcha_answer(img)
    print(f'获取到验证码答案:{answer}')
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
    """
    req = request.form.to_dict()
    try:
        clock = Clock(args=req)
    except KeyError as err:
        res = {
            "code": "401",
            "ok": "false",
            "msg": f'参数{err.args[0]}没有填写'
        }
    except const.LoginErr:
        res = {
            "code": "401",
            "ok": "false",
            "msg": "登录失败"
        }
    except const.GET_MIDDLE_COOKIE_ERR:
        res = {
            "code": "401",
            "ok": "false",
            "msg": "获取中间cookie失败"
        }
    except const.UPDATE_WEU_ERR:
        res = {
            "code": "401",
            "ok": "false",
            "msg": r'更新 "_WEU" cookie失败'
        }
    except const.GET_CLOCK_HISTORY_ERR:
        res = {
            "code": "401",
            "ok": "false",
            "msg": "获取打卡历史失败"
        }
    else:
        print('获取cookie成功')
        clock.clock_on(clock_date=datetime.datetime.now(), force=False)
        res = {
            "code": "200",
            "ok": "true",
            "msg": "打卡成功"
        }
        return jsonify(res), 200
    return jsonify(res), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089, debug=True)
