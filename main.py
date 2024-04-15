import paho.mqtt.client as mqtt
import time
from rs485_hien import *
import smtplib

MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = "mse14-group6"
MQTT_PASSWORD = "1234"
MQTT_TOPIC_PUB = [f"{MQTT_USERNAME}/feeds/temperature", f"{MQTT_USERNAME}/feeds/moisture"]
MQTT_TOPIC_SUB = [f"{MQTT_USERNAME}/feeds/relay02", f"{MQTT_USERNAME}/feeds/relay03", f"{MQTT_USERNAME}/feeds/relay04"]

temperature_index = 0
moisture_index = 1
sensors_and_actuators = SensorsAndActuators()


def mqtt_connected(client, userdata, flags, rc):
    for feed in MQTT_TOPIC_SUB:
        client.subscribe(feed)
    print("Connected successfully!!")


def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")


def message(client, feed_id, payload):
    print("Received: " + str(payload.payload.decode('utf-8')))
    print("Received:", message)

    # Xác định relay và trạng thái từ dữ liệu MQTT
    if feed_id == MQTT_TOPIC_SUB[0]:  # Nếu là topic relay02
        relay_number = 2
    elif feed_id == MQTT_TOPIC_SUB[1]:  # Nếu là topic relay03
        relay_number = 3
    elif feed_id == MQTT_TOPIC_SUB[2]:  # Nếu là topic relay04
        relay_number = 4
    else:
        return

    # Bật hoặc tắt relay tương ứng
    if message.lower() == "on":
        relay_state = True
    elif message.lower() == "off":
        relay_state = False
    else:
        return

    # Gọi hàm set_relay để thực hiện bật hoặc tắt relay
    sensors_and_actuators.set_relay(relay_number, relay_state)


mqttClient = mqtt.Client()
mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

# Register mqtt events
mqttClient.on_connect = mqtt_connected
mqttClient.on_subscribe = mqtt_subscribed
mqttClient.on_message = message
mqttClient.loop_start()

counter = 0
while True:
    temperature = round(sensors_and_actuators.read_temperature() * 0.01, 2)
    print(f"Nhiet do:", temperature)
    mqttClient.publish(MQTT_TOPIC_PUB[temperature_index], temperature)

    moisture = round(sensors_and_actuators.read_moisture(), 2)
    print(f"Do am:", moisture)
    mqttClient.publish(MQTT_TOPIC_PUB[moisture_index], moisture)
    time.sleep(1)

    if temperature > 27.50:
        sender_email = "hien.ortholite@gmail.com"
        receiver_email = "hien.ortholite@gmail.com"
        password = "enrj wehd seju scjf"

        print(f"Nhiet do:", temperature)
        message = """\
        Subject: Temperature Alert

        The temperature is above 27.50°C. Please take necessary action."""

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
