import functools

import paho.mqtt.client as mqtt
import time
import json
import os
import math
import pms5003

PMS_5003 = pms5003.PMS5003()

def pm25_to_aqi(pm25):
    lower_bound_pm25 = None
    upper_bound_pm25 = 0
    lower_bound_aqi = None
    upper_bound_aqi = 0
    aqi_cat = ''
    for cat, cutoff, aqi_val in [('good', 12.1, 50), ('moderate', 35.5, 100), ('usg', 55.5, 150), ('unhealthy', 150.5, 200), ('very unhealthy', 250.5, 300), ('hazardous', 350.5, 400), ('wtf', 9999999, 500)]:
        aqi_cat = cat
        lower_bound_aqi = upper_bound_aqi
        lower_bound_pm25 = upper_bound_pm25
        upper_bound_aqi = aqi_val
        upper_bound_pm25 = cutoff
        if pm25 < cutoff:
            break
    aqi = (pm25 - lower_bound_pm25) * (upper_bound_aqi - lower_bound_aqi) / (upper_bound_pm25 - lower_bound_pm25) + lower_bound_aqi
    aqi = math.ceil(aqi)
    return aqi_cat, aqi


def publish_pms5003(mqtt_client):
    result = PMS_5003.read()
    values = {
        'pm1': result.pm_ug_per_m3(1),
        'pm25': result.pm_ug_per_m3(2.5),
        'pm10': result.pm_ug_per_m3(10),
    }
    values['aqi_cat'], values['aqi'] = pm25_to_aqi(result.pm_ug_per_m3(2.5))

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
