FROM bitnami/pytorch:1.12.1

EXPOSE 8089

WORKDIR /src

COPY . /src
RUN unset LD_PRELOAD
#RUN sudo chown -R root /.cache/pip/
#RUN sudo -H pip3 install --upgrade -r requirements.txt
#
#CMD python /src/server.py