import functools
from typing import Optional

import paho.mqtt.client as mqtt
import os
import subprocess
import time
import cv2
import tflite_runtime.interpreter as tflite
import numpy as np

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


def make_big_light_controller(mqtt_client):
    interpreter = tflite.Interpreter(model_path='biglight_model.tflite')
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    floating_model = (input_details[0]['dtype'] == np.float32)

    def on_off_cmd():
        subprocess.check_call("ir-ctl -S nec:0x404", shell=True)

    def poll_cmd():
        start = time.time()
        photo = take_photo()
        model_start = time.time()

        input_data = np.expand_dims(cv2.cvtColor(photo, cv2.COLOR_BGR2RGB), axis=0)
        if floating_model:
            input_data = input_data.astype('float32')

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        prob_on = interpreter.get_tensor(output_details[0]['index'])[0][1]

        end = time.time()
        print(f'Poll result: {prob_on}: took {model_start - start:.2f} for photo; {end - model_start:.2f} for model')
        if 0.7 <= prob_on <= 0.3:
            filename = f'/photos/big_light_no_conf/{time.time()}.jpg'
            print(f'No confidence in prediction: {prob_on}. Saving file to {filename}.')

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            cv2.imwrite(filename, photo)

            return None

        return prob_on >= 0.5

    return controller.LightController(
        'Big Light',
        mqtt_client=mqtt_client,
        mqtt_status_topic='home/living/light/status',
        on_or_off_cmd=on_off_cmd,
        poll_cmd=poll_cmd,
        on_repeat_delay=3,
        off_repeat_delay=3,
        max_repeat_time=10,
        poll_interval=30,
    )


BIG_LIGHT_CONTROLLER : Optional[controller.LightController] = None


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
            BIG_LIGHT_CONTROLLER.mqtt_message(msg.payload)
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

    global TV_CONTROLLER, BIG_LIGHT_CONTROLLER

    TV_CONTROLLER = make_tv_controller(client)
    TV_CONTROLLER.start()

    BIG_LIGHT_CONTROLLER = make_big_light_controller(client)
    BIG_LIGHT_CONTROLLER.start()

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == '__main__':
    main()
