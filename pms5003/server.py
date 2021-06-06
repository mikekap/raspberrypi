import functools

import paho.mqtt.client as mqtt
import pms5003
import time
import json

PMS_5003 = pms5003.PMS5003()

def publish_pms5003(mqtt_client):
    result = PMS_5003.read()
    values = {
        'pm1': result.pm_ug_per_m3(1),
        'pm25': result.pm_ug_per_m3(2.5),
        'pm10': result.pm_ug_per_m3(10),
    }

    mqtt_client.publish('home/bedroom/air_quality', json.dumps(values))

def main():
    client = mqtt.Client()

    client.connect(os.environ.get('MQTT_HOST', "raspberrypi"), 1883, 60)
    client.loop_start()
    try:
        while True:
            publish_pms5003()
            time.sleep(10)
    finally:
        client.loop_stop()

if __name__ == '__main__':
    main()
