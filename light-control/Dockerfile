FROM rpi-base

RUN apt install -y v4l-utils

ADD requirements.txt /
RUN python3 -m pip install -r requirements.txt

ADD mikes-light.toml /
ADD server.py /

CMD ["python3", "/server.py"]
