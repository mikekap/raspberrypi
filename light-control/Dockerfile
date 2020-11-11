FROM rpi-base

RUN apt install -y v4l-utils iputils-ping python3-opencv --no-install-recommends

ADD requirements.txt /
RUN python3 -m pip install -r requirements.txt

ADD mikes-light.toml /
ADD server.py /

CMD ["python3", "-u", "/server.py"]
