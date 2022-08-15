import json
import captcha as c

from flask import Flask, request, Response, jsonify

app = Flask('jwzx')


@app.route('/captcha', methods=['get'])
def captcha():
    timestamp = request.args.get('timestamp')
    session_id = request.args.get('session_id')
    route = request.args.get('route')
    # 通过时间戳和session_id获取对应的captcha
    img = c.get_captcha_img(timestamp, session_id, route)
    # 获取对应captcha的answer
    answer = c.get_captcha_answer(img)
    print(answer)
    res = {
        "code": "200",
        "ok": "true",
        "data": answer
    }
    return jsonify(res)


@app.route('/do',methods=['post'])
def do():
    print(1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089, debug=True)
