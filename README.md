```
docker build -t cqupt-clock .
```

```
docker run -it \
-p 8089:8089 \
-d \
--restart=always \
--name cqupt-clock \
-v /www/wwwroot/jwzx.stellaris.wang:/workspace \ # 改一下项目代码文件放得位置
--entrypoint=/bin/bash \
cqupt-clock \
python main.py
```