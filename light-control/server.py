import paho.mqtt.client as mqtt
import os
import subprocess

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("home/living/light/#")
    client.subscribe("home/living/tv/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic.startswith('home/living/light'):
        if msg.topic.endswith('/toggle'):
            print('power-light', str(msg.payload))
            subprocess.check_call("ir-ctl -S nec:0x404", shell=True)
        if msg.topic.endswith('/toggle-night'):
            print('power-night', str(msg.payload))
            subprocess.check_call("ir-ctl -S nec:0x405", shell=True)
    elif msg.topic.startswith('home/living/tv'):
        if msg.topic.endswith('/toggle'):
            print('power-tv', str(msg.payload))
            subprocess.check_call('ir-ctl -S necx:0x70702', shell=True)

    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.environ.get('MQTT_HOST', "raspberrypi"), 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
