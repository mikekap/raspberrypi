import collections
import functools
import os
import queue
import threading
import time
import traceback
import typing

import paho.mqtt.client as mqtt


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


PollStatus = collections.namedtuple('PollStatus', "up")
Command = collections.namedtuple('Command', "up")


class LightController(threading.Thread):
    def __init__(self,
                 name,
                 on_or_off_cmd: typing.Callable[[], None],
                 poll_cmd: typing.Callable[[], bool],
                 mqtt_client: mqtt.Client,
                 mqtt_status_topic,
                 *,
                 on_repeat_delay=22,
                 off_repeat_delay=1,
                 max_repeat_time=60,
                 poll_interval=2):
        super().__init__(daemon=True)
        self.name = name
        self.on_or_off_cmd = on_or_off_cmd
        self.poll_cmd = poll_cmd
        self.q = queue.Queue(100)
        self.mqtt_client = mqtt_client
        self.mqtt_status_topic = mqtt_status_topic
        self.last_control_message = False
        self.last_control_message_timestamp = 0.0
        self.last_ping_status = False
        self.last_ir_send_timestamp = 0.0

        self.on_repeat_delay = on_repeat_delay
        self.off_repeat_delay = off_repeat_delay
        self.max_repeat_time = max_repeat_time
        self.poll_interval = poll_interval

    def start(self):
        super(LightController, self).start()
        threading.Thread(target=self.poll_loop, daemon=True).start()

    @thread_loop
    def poll_loop(self):
        interval = self.poll_interval

        while True:
            start = time.time()
            alive = self.poll_cmd()
            try:
                self.q.put_nowait(PollStatus(alive))
            except queue.Full:
                pass

            elapsed = (time.time() - start)
            if elapsed < interval:
                time.sleep(interval - elapsed)

    def send_ir(self, first=False):
        print(f'{self.name}: Firing IR')
        self.on_or_off_cmd()
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

            if isinstance(item, Command):
                self.last_control_message = item.up
                self.last_control_message_timestamp = time.time()
                if item.up != self.last_ping_status:
                    self.send_ir(True)
            elif isinstance(item, PollStatus):
                was_waiting = self.waiting_for_ir_to_complete()
                was_up = self.last_ping_status
                self.last_ping_status = item.up

                if self.waiting_for_ir_to_complete():
                    print(f'{self.name}: Waiting for status to change to {item.up}')
                    self.maybe_resend_ir_message()
                else:
                    if was_waiting:
                        print(f'{self.name}: Finished waiting for command completion; took {time.time() - self.last_control_message_timestamp:.2f}')
                    if was_up != self.last_ping_status:
                        print(f'{self.name}: Changed status from {was_up} to {self.last_ping_status}')
                    self.mqtt_client.publish(self.mqtt_status_topic, b'ON' if self.last_ping_status else b'OFF')

            self.q.task_done()

    def mqtt_message(self, contents):
        self.q.put(Command(True if b'ON' in contents else False))
