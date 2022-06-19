FROM rpi-base

RUN apt install -y v4l-utils iputils-ping python3-opencv --no-install-recommends

ADD tflite_runtime*.whl .
ADD requirements.txt /
RUN python3 -m pip install -r requirements.txt

ADD mikes-light.toml /server/
ADD *.py /server/
ADD *.tflite /

CMD ["python3", "-u", "-m", "server.server"]
