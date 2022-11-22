#!/bin/bash

if [ "${ENABLE_CRON}" = "true" ];then
  python main.py & python ./cron/cron.py
else

  python main.py
fi