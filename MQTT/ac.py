import paho.mqtt.client as mqtt
# from Crypto.Cipher import AES
# from crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from time import time
import json
import cipher

# MQTT settings
BROKER = "127.0.0.1"
PORT = 1883
TOPIC_AC_STATUS = "ac1/status"
TOPIC_AC_COMMAND = "ac1/command"
TOPIC_BIND_REQUEST = "bind/request"
TOPIC_BIND_RESPONSE = "bind/response"
ssid = 1

# Initialize switch status
ac_status = "off"
binded = False

# Create client instance
client = mqtt.Client()

#连接
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(TOPIC_AC_STATUS)
        client.subscribe(TOPIC_AC_COMMAND)
        client.subscribe(TOPIC_BIND_REQUEST)
        client.subscribe(TOPIC_BIND_RESPONSE)
    else:
        print(f"Connection failed with code {rc}")


#接收到的消息
def on_message(client, userdata, message):
    global ac_status
    msg =cipher.decrypt_and_validate_message(message.payload)  # 60 seconds allowed time window
    command = msg.split()  # 拆分msg
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    # msg = message.payload.decode()
    # command = msg.split()  # 拆分msg

    # 打印接收到的消息
    #print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

    #绑定消息
    if message.topic == "bind/request":

        if command[1] == "ac":
            if command[2] == str(ssid):
                binded = True
                #发布消息：绑定成功，灯状态
                # response_msg = f"Ac bind to {ssid} successful！"
                # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                encrypted_response = cipher.encrypt_message(f"Ac bind to {ssid} successful！", timestamp)
                client.publish(TOPIC_BIND_RESPONSE, encrypted_response)
                encrypted_status = cipher.encrypt_message(ac_status, timestamp)
                client.publish(TOPIC_AC_STATUS, encrypted_status)
                # client.publish(TOPIC_BIND_RESPONSE, f"Ac bind to {ssid} successful！")
                # client.publish(TOPIC_AC_STATUS, ac_status)
                print(f"Ac bind to {ssid} successful！")
            else:
                print("Bind ac error!")

    #控制消息
    if message.topic == "ac1/command":
        if command[0] == "on":
            ac_status = "on"
            print("Ac turned on")
            # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            encrypted_status = cipher.encrypt_message(ac_status, timestamp)
            client.publish(TOPIC_AC_STATUS, encrypted_status)
            # client.publish(TOPIC_AC_STATUS, ac_status)

        elif command[0] == "off":
            ac_status = "off"
            print("Ac turned off")
            # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            encrypted_status = cipher.encrypt_message(ac_status, timestamp)
            client.publish(TOPIC_AC_STATUS, encrypted_status)
            # client.publish(TOPIC_AC_STATUS, ac_status)



client.on_connect = on_connect
client.on_message = on_message

#连接MQTT服务器
client.connect(BROKER, PORT, 60)
client.loop_forever()

