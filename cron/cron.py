import json
import os
from backports import zoneinfo
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

port = os.getenv("CLOCK_PORT")
if port is None:
    port = 8089
do_url = f'http://localhost:{str(port)}/do'


def my_job():
    with open('./cron/info.json', 'r+', encoding='utf-8') as f:
        j = json.load(f)
    _ = requests.post(
        url=do_url,
        data=j
    )


if __name__ == '__main__':
    # 读取文件
    hour = os.getenv("CRON_HOUR")
    if hour is None:
        hour = 12
    else:
        hour = int(hour)

    jitter = os.getenv("CRON_JITTER")
    if jitter is None:
        jitter = 3600
    else:
        jitter = int(jitter)

    timezone = zoneinfo.ZoneInfo("Asia/Shanghai")
    scheduler = BlockingScheduler()
    scheduler.add_job(my_job, 'cron', hour=hour, jitter=jitter,
                      timezone=timezone)
    scheduler.start()
