import json
import os
import zoneinfo
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

do_url = "http://localhost:8089/do"


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

    timezone = zoneinfo.ZoneInfo("Asia/Shanghai")
    scheduler = BlockingScheduler()
    scheduler.add_job(my_job, 'cron', kwargs=j, hour=os.getenv("CRON_HOUR"), jitter=os.getenv("CRON_JITTER"),
                      timezone=timezone)
    scheduler.start()
