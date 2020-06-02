FROM rpi-base

RUN apt update && apt install -y v4l-utils && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD mikes-light.toml /
ADD server.py /

RUN ["python", "server.py"]
