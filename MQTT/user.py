import json
from datetime import datetime
import paho.mqtt.client as mqtt
from cryptography.fernet import Fernet

import cipher

# MQTT设置
BROKER = "127.0.0.1"  # MQTT服务器IP
PORT = 1883

id_switch = 1
id_light = 1
id_ac = 1


def generate_topic_status(base_topic, id):
    return f"{base_topic}{id}/status"
def generate_topic_command(base_topic, id):
    return f"{base_topic}{id}/command"

# 主题设置
#TOPIC_SWITCH_STATUS = "switch/status"
TOPIC_SWITCH_STATUS = generate_topic_status("switch", id_switch)


#TOPIC_SWITCH_COMMAND = "switch/command"
TOPIC_SWITCH_COMMAND = generate_topic_command("switch", id_switch)

#TOPIC_LIGHT_STATUS = "light/status"
TOPIC_LIGHT_STATUS = generate_topic_status("light", id_light)

#TOPIC_LIGHT_COMMAND = "light/command"
TOPIC_LIGHT_COMMAND = generate_topic_command("light", id_light)

#TOPIC_AC_STATUS = "ac/status"
TOPIC_AC_STATUS = generate_topic_status("ac", id_ac)

#TOPIC_AC_COMMAND = "ac/command"
TOPIC_AC_COMMAND = generate_topic_command("ac", id_ac)


TOPIC_BIND_REQUEST = "bind/request"
TOPIC_BIND_RESPONSE = "bind/response"

# 初始化
switch_status = "not connected"
switch_connected = False
light_status = "not connected"
light_connected = False
ac_status = "not connected"
ac_connected = False

# 创建客户端实例
client = mqtt.Client()


# 连接处理逻辑
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        # 订阅主题
        client.subscribe(TOPIC_SWITCH_STATUS)
        client.subscribe(TOPIC_LIGHT_STATUS)
        client.subscribe(TOPIC_AC_STATUS)
        client.subscribe(TOPIC_SWITCH_COMMAND)
        client.subscribe(TOPIC_LIGHT_COMMAND)
        client.subscribe(TOPIC_AC_COMMAND)
        client.subscribe(TOPIC_BIND_REQUEST)
        client.subscribe(TOPIC_BIND_RESPONSE)
    else:
        print(f"Connection failed with code {rc}")


# 接收到的消息
def on_message(client, userdata, message):
    global switch_status, light_status, ac_status, switch_connected, light_connected, ac_connected
    # msg = message.payload.decode()
    msg = cipher.decrypt_and_validate_message(message.payload)  # 解密
    command = msg.split()  # 拆分msg
    #print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

    # "Switch bind to {ssid} seccessful！"
    if message.topic == "bind/response":
        if command[4] == "successful！":
            device = command[0]  # 从主题中提取设备类型
            if device == "Switch":
                switch_connected = True
                print(f"Switch {command[3]} bound.")

            elif device == "Light":
                light_connected = True
                print(f"Light {command[3]} bound.")
                print(generate_topic_status("light", id_light))

            elif device == "Ac":
                ac_connected = True
                print(f"Ac {command[3]} bound.")

    if switch_connected and message.topic == generate_topic_status("switch", id_switch):
        switch_status = msg
    # elif light_connected and message.topic == generate_topic_status("light", id_light):
    elif light_connected and message.topic == "light1/status":
        light_status = msg
        print(f"Updated light status: {light_status}")
    elif ac_connected and message.topic == generate_topic_status("ac", id_ac):
        ac_status = msg


client.on_connect = on_connect
client.on_message = on_message

# 连接MQTT服务器
client.connect(BROKER, PORT, 60)
# 开始网络循环，保持连接并处理消息
client.loop_start()

while True:
    message = input("Enter command (bind <device> <ssid>, switch on/off, light on/off, ac on/off, status, exit): ")
    command = message.split()  # 拆分message
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if command[0] == "bind":
        # bind <device> <ssid>
        # client.publish(TOPIC_BIND_REQUEST, f"{command[0]} {command[1]} {command[2]}")
        encrypted_response = cipher.encrypt_message(f"{command[0]} {command[1]} {command[2]}", timestamp)
        client.publish(TOPIC_BIND_REQUEST, encrypted_response)

        if command[1] == "switch":
            # id_switch = input()  # 模拟用户通过扫描设备二维码获取设备id信息
            id_switch = command[2]
            TOPIC_SWITCH_COMMAND = generate_topic_command("switch", id_switch)
            TOPIC_SWITCH_STATUS = generate_topic_status("switch", id_switch)
            print("User wants to bind the switch.")

        elif command[1] == "light":
            #id_light = input() # 模拟用户通过扫描设备二维码获取设备id信息
            id_light = command[2]
            TOPIC_LIGHT_COMMAND = generate_topic_command("light", id_light)
            TOPIC_LIGHT_STATUS = generate_topic_status("light", id_light)
            print("User wants to bind the light.")

        elif command[1] == "ac":
            #id_ac = input()  # 模拟用户通过扫描设备二维码获取设备id信息
            id_ac = command[2]

            TOPIC_AC_COMMAND = generate_topic_command("ac", id_ac)
            TOPIC_AC_STATUS = generate_topic_status("ac", id_ac)
            print("User wants to bind the ac.")

        else:
            print("Invalid device.")

    elif command[0] == "switch":
        if switch_connected:
            if command[1] == "on":
                print("User wants to turn on the switch.")
                # client.publish(TOPIC_SWITCH_COMMAND, "on")
                encrypted_response = cipher.encrypt_message("on", timestamp)
                client.publish(TOPIC_SWITCH_COMMAND, encrypted_response)
            elif command[1] == "off":
                print("User wants to turn off the switch.")
                # client.publish(TOPIC_SWITCH_COMMAND, "off")
                encrypted_response = cipher.encrypt_message("off", timestamp)
                client.publish(TOPIC_SWITCH_COMMAND, encrypted_response)
        else:
            print("Please bind the switch first.")

    elif command[0] == "light":
        if light_connected:
            if command[1] == "on":
                print("User wants to turn on the light.")
                # client.publish(TOPIC_LIGHT_COMMAND, "on")
                encrypted_response = cipher.encrypt_message("on", timestamp)
                client.publish(TOPIC_LIGHT_COMMAND, encrypted_response)
            elif command[1] == "off":
                print("User wants to turn off the light.")
                # client.publish(TOPIC_LIGHT_COMMAND, "off")
                encrypted_response = cipher.encrypt_message("off", timestamp)
                client.publish(TOPIC_LIGHT_COMMAND, encrypted_response)
        else:
            print("Please bind the light first.")

    elif command[0] == "ac":
        if ac_connected:
            if command[1] == "on":
                print("User wants to turn on the ac.")
                # client.publish(TOPIC_AC_COMMAND, "on")
                encrypted_response = cipher.encrypt_message("on", timestamp)
                client.publish(TOPIC_AC_COMMAND, encrypted_response)
            elif command[1] == "off":
                print("User wants to turn off the ac.")
                # client.publish(TOPIC_AC_COMMAND, "off")
                encrypted_response = cipher.encrypt_message("off", timestamp)
                client.publish(TOPIC_AC_COMMAND, encrypted_response)
        else:
            print("Please bind the air conditioning first.")

    elif command[0] == "status":
        print(f"---------------------------------")
        print(f"Switch          : {switch_status}")
        print(f"Light           : {light_status}")
        print(f"Air Conditioner : {ac_status}")
        print(f"---------------------------------")

    elif command[0] == "exit":
        break

    else:
        print("Invalid command.")
