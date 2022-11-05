import paho.mqtt.client as mqtt
import json
import time, datetime
import busio
import board
import digitalio
from adafruit_pm25.i2c import PM25_I2C
import adafruit_pct2075

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
reset_pin=None
pm25 = PM25_I2C(i2c, reset_pin)
pct = adafruit_pct2075.PCT2075(i2c)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def discovery_topic_for(ident):
    return f'homeassistant/sensor/{ident}/config';

def state_topic_for(ident):
    return f'home/sensor/{ident}/value'

outside_particulate_id = 'atmosphereBoiParticulate'
outside_particulate_state_topic = state_topic_for(outside_particulate_id)

outside_pm1_discovery_topic = discovery_topic_for(f'{outside_particulate_id}_pm1')
pm1_config = {
    'name': 'Outside PM1.0',
    'stat_t': outside_particulate_state_topic,
    'unit_of_meas': 'µg/m³',
    'dev_cla': 'pm1',
    'frc_upd': True,
    'val_tpl': '{{ value_json.pm1|default(0) }}',
};

outside_pm25_discovery_topic = discovery_topic_for(f'{outside_particulate_id}_pm25')
pm25_config = {
    'name': 'Outside PM2.5',
    'stat_t': outside_particulate_state_topic,
    'unit_of_meas': 'µg/m³',
    'dev_cla': 'pm25',
    'frc_upd': True,
    'val_tpl': '{{ value_json.pm25|default(0) }}',
};

outside_pm10_discovery_topic = discovery_topic_for(f'{outside_particulate_id}_pm10')
pm10_config = {
    'name': 'Outside PM10.0',
    'stat_t': outside_particulate_state_topic,
    'unit_of_meas': 'µg/m³',
    'dev_cla': 'pm10',
    'frc_upd': True,
    'val_tpl': '{{ value_json.pm10|default(0) }}',
};

outside_temperature_id = 'outdoorTemperature'
outside_temperature_state_topic = state_topic_for(outside_particulate_id)

outside_temperature_discovery_topic = discovery_topic_for(f'{outside_temperature_id}_temperature')
temperature_config = {
    'name': 'Outside Temperature',
    'stat_t': outside_temperature_state_topic,
    'unit_of_meas': '˚F',
    'dev_cla': 'temperature',
    'frc_upd': True,
    'val_tpl': '{{ value_json.temperature|default(0) }}',
};

configs = {
    'pm1': {
        'state_topic': outside_particulate_state_topic,
        'discovery_topic': outside_pm1_discovery_topic,
        'config': pm1_config,
    },
    'pm25': {
        'state_topic': outside_particulate_state_topic,
        'discovery_topic': outside_pm25_discovery_topic,
        'config': pm25_config,
    },
    'pm10': {
        'state_topic': outside_particulate_state_topic,
        'discovery_topic': outside_pm10_discovery_topic,
        'config': pm10_config,
    },
    'temperature': {
        'state_topic': outside_temperature_state_topic,
        'discovery_topic': outside_temperature_discovery_topic,
        'config': temperature_config,
    },
}

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.20", 1883, 60)

for key, meta in configs.items():
    client.publish(
        meta['discovery_topic'],
        json.dumps(meta['config']),
        retain=True,
    )

while True:
    time.sleep(1)

    temperatureData = {
        "temperature": pct.temperature,
    }

    client.publish(configs['temperature']['state_topic'], json.dumps(temperatureData))
    print(temperatureData)

    try:
        aqdata = pm25.read()
        pmData = {
            "pm1": aqdata["pm10 standard"],
            "pm25": aqdata["pm25 standard"],
            "pm10": aqdata["pm100 standard"],
        }
        client.publish(configs['pm1']['state_topic'], json.dumps(pmData))
        print(pmData)
    except RuntimeError:
        pass
