import paho.mqtt.client as mqtt
import os
import subprocess

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("home/living/light/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic.endswith('/toggle'):
        print('power',str(msg.payload))
        subprocess.check_call("ir-ctl -S nec:0x404", shell=True)

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
