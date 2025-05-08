import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from heatstroke import settings
import json
from sensor.models import SensorData
import ssl

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    payload = msg.payload.decode()
    print(f'Received message on topic: {msg.topic} with payload: {payload}')
    data = json.loads(payload)

    SensorData.objects.create(
        user = data.get("user"),
        heart_rate = data.get("heart_rate"),
        skin_temperature = data.get("skin_temperature"),
        ambient_temperature = data.get("ambient_temperature"),
        humidity = data.get("humidity"),
        skin_resistance = data.get("skin_resistance"),
        risk  = data.get("risk")
    )

    #ส่งข้อมูลไปให้เว็ปก่อน
    #แล้วค่อยเอาไปเก็บใน db


class Command(BaseCommand):
    help = "MQTT start listening!!!"

    def handle(self, *args, **options):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
        client.tls_set("../../../emqxsl-ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
        client.connect(
            host=settings.MQTT_SERVER,
            port=settings.MQTT_PORT,
            keepalive=settings.MQTT_KEEPALIVE
        )
        client.loop_forever()