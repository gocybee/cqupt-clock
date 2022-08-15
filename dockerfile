FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime

EXPOSE 8089

WORKDIR /src

COPY . /src
RUN unset LD_PRELOAD
#RUN sudo chown -R root /.cache/pip/
#RUN sudo -H pip3 install --upgrade -r requirements.txt
RUN pip install pycryptodomex
RUN pip selenium
#
#CMD python /src/server.py