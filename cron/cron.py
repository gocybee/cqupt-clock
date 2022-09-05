import json
import os
from backports import zoneinfo
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

port = os.getenv("CLOCK_PORT")
if port is None:
    port = 8089
do_url = f'http://localhost:{port}/do'


def my_job(**kwargs):
    res = requests.post(
        url=do_url,
        data=kwargs
    )
    print(res.text)


if __name__ == '__main__':
    # 读取文件
    with open('info.json', 'r+', encoding='utf-8') as f:
        j = json.load(f)
    hour = os.getenv("CRON_HOUR")
    if hour is None:
        hour = 12
    jitter = os.getenv("CRON_JITTER")
    if jitter is None:
        jitter = 3600
    timezone = zoneinfo.ZoneInfo("Asia/Shanghai")
    scheduler = BlockingScheduler()
    scheduler.add_job(my_job, 'cron', kwargs=j, hour=hour, jitter=jitter,
                      timezone=timezone)
    scheduler.start()
