import functools
from typing import Optional

import paho.mqtt.client as mqtt
import collections
import os
import subprocess
import queue
import sys
import traceback
import threading
import time
improt cv2


def thread_loop(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            while True:
                fn(*args, **kwargs)
        except:
            traceback.print_exc()
            os._exit(1)
    return wrapped


TvPingStatus = collections.namedtuple('TvPingStatus', "up")
TvCommand = collections.namedtuple('TvCommand', "up")

class TvController(threading.Thread):
    def __init__(self, mqtt_client: mqtt.Client):
        super().__init__(daemon=True)
        self.q = queue.Queue(100)
        self.mqtt_client = mqtt_client
        self.last_control_message = False
        self.last_control_message_timestamp = 0.0
        self.last_ping_status = False
        self.last_ir_send_timestamp = 0.0

        self.on_repeat_delay = 22
        self.off_repeat_delay = 1
        self.max_repeat_time = 60

    def start(self):
        super(TvController, self).start()
        threading.Thread(target=self.tv_ping_loop, daemon=True).start()

    @thread_loop
    def tv_ping_loop(self):
        interval = 2.0

        while True:
            start = time.time()
            retcode = subprocess.call(["ping", "-W", "2", "-c", "1", "samsungtv"], stdout=subprocess.DEVNULL)
            try:
                if retcode:
                    self.q.put_nowait(TvPingStatus(False))
                else:
                    self.q.put_nowait(TvPingStatus(True))
            except queue.Full:
                pass

            elapsed = (time.time() - start)
            if elapsed < interval:
                time.sleep(interval - elapsed)

    def send_ir(self, first=False):
        print('TV Firing IR blaster')
        subprocess.check_call('ir-ctl -S necx:0x70702 -S necx:0x70702 -S necx:0x70702', shell=True)
        self.last_ir_send_timestamp = time.time()

    def waiting_for_ir_to_complete(self):
        return self.last_control_message_timestamp + self.max_repeat_time >= time.time() and self.last_ping_status != self.last_control_message

    def maybe_resend_ir_message(self):
        delay = self.on_repeat_delay if self.last_control_message else self.off_repeat_delay
        if self.last_ir_send_timestamp + delay <= time.time():
            self.send_ir()

    @thread_loop
    def run(self):
        while True:
            item = self.q.get()

            if isinstance(item, TvCommand):
                self.last_control_message = item.up
                self.last_control_message_timestamp = time.time()
                if item.up != self.last_ping_status:
                    self.send_ir(True)
            elif isinstance(item, TvPingStatus):
                was_waiting = self.waiting_for_ir_to_complete()
                was_up = self.last_ping_status
                self.last_ping_status = item.up

                if self.waiting_for_ir_to_complete():
                    print('Waiting for IR...', item.up)
                    self.maybe_resend_ir_message()
                else:
                    if was_waiting:
                        print(f'Finished waiting for command completion; took {time.time() - self.last_control_message_timestamp:.2f}')
                    if was_up != self.last_ping_status:
                        print(f'Changed status from {was_up} to {self.last_ping_status}')
                    self.mqtt_client.publish('home/living/tv/status', b'ON' if self.last_ping_status else b'OFF')

            self.q.task_done()

    def mqtt_message(self, contents):
        self.q.put(TvCommand(True if b'ON' in contents else False))


TV_CONTROLLER : Optional[TvController] = None


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

    TV_CONTROLLER = TvController(client)
    TV_CONTROLLER.start()

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == '__main__':
    main()
