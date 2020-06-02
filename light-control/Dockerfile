FROM rpi-base

RUN apt install -y v4l-utils

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD mikes-light.toml /
ADD server.py /

RUN ["python", "server.py"]
