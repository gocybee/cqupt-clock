FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime

EXPOSE 8089
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

COPY . /workspace
# 安装python依赖包
RUN pip install flask -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install selenium -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install browser-cookie3 -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install matplotlib -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install apscheduler -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install thefuzz -i https://mirrors.aliyun.com/pypi/simple/
# 更新apt-get源
RUN cp ./dependency/sources.list /etc/apt/sources.list
RUN apt-get update
# 安装chrome环境
RUN apt-get --fix-broken install -y ./dependency/google-chrome-stable_current_amd64.deb
RUN cp ./dependency/chromedriver /usr/bin
RUN chmod +x /usr/bin/chromedriver
# 设置系统时区
RUN apt-get install -y tzdata # 该镜像没有zoneinfo文件夹
RUN rm -f /etc/localtime
RUN ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN chmod +x ./run.sh

CMD ["./run.sh"]