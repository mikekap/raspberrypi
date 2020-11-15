import functools
from typing import Optional

import paho.mqtt.client as mqtt
import os
import subprocess
import time
import cv2

from . import controller


def make_tv_controller(mqtt_client):
    def on_off_cmd():
        subprocess.check_call('ir-ctl -S necx:0x70702 -S necx:0x70702 -S necx:0x70702', shell=True)

    def ping_cmd():
        retcode = subprocess.call(["ping", "-W", "2", "-c", "1", "samsungtv"], stdout=subprocess.DEVNULL)
        return False if retcode else True

    return controller.LightController(
        'TV',
        mqtt_client=mqtt_client,
        mqtt_status_topic='home/living/tv/status',
        on_or_off_cmd=on_off_cmd,
        poll_cmd=ping_cmd,
        on_repeat_delay=22,
        off_repeat_delay=1,
        max_repeat_time=60,
        poll_interval=2,
    )


TV_CONTROLLER : Optional[controller.LightController] = None


def take_photo():
    cap = cv2.VideoCapture(0 + cv2.CAP_V4L)
    try:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, 0.1)

        return cap.read()[1]
    finally:
        cap.release()


def write_payload_photo_file(type, payload):
    payload = payload.decode('utf-8').strip()
    os.makedirs(f'/photos/{type}/{payload}', exist_ok=True)
    cv2.imwrite(f'/photos/{type}/{payload}/{time.time()}.jpg', take_photo())


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("home/living/light/toggle")
    client.subscribe("home/living/light/toggle-night")
    client.subscribe("home/living/light/record")
    client.subscribe("home/living/light/record-night")
    client.subscribe("home/living/tv/toggle")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic.startswith('home/living/light'):
        if msg.topic.endswith('/toggle'):
            print('power-light', str(msg.payload))
            subprocess.check_call("ir-ctl -S nec:0x404", shell=True)
        if msg.topic.endswith('/toggle-night'):
            print('power-night', str(msg.payload))
            subprocess.check_call("ir-ctl -S nec:0x405", shell=True)
        if msg.topic.endswith('/record'):
            write_payload_photo_file('light', msg.payload)
        if msg.topic.endswith('/record-night'):
            write_payload_photo_file('night', msg.payload)

    elif msg.topic.startswith('home/living/tv'):
        if msg.topic.endswith('/toggle'):
            print('power-tv', str(msg.payload))
            TV_CONTROLLER.mqtt_message(msg.payload)

    print(msg.topic+" "+str(msg.payload))


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(os.environ.get('MQTT_HOST', "raspberrypi"), 1883, 60)

    global TV_CONTROLLER

    TV_CONTROLLER = make_tv_controller(client)
    TV_CONTROLLER.start()

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == '__main__':
    main()
