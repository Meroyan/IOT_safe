from datetime import datetime

import paho.mqtt.client as mqtt
import cipher
# MQTT settings
BROKER = "127.0.0.1"
PORT = 1883
TOPIC_SWITCH_STATUS = "switch1/status"
TOPIC_SWITCH_COMMAND = "switch1/command"
TOPIC_BIND_REQUEST = "bind/request"
TOPIC_BIND_RESPONSE = "bind/response"
ssid = 1

# Initialize switch status
switch_status = "off"
binded = False

# Create client instance
client = mqtt.Client()


#连接
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(TOPIC_SWITCH_STATUS)
        client.subscribe(TOPIC_SWITCH_COMMAND)
        client.subscribe(TOPIC_BIND_REQUEST)
        client.subscribe(TOPIC_BIND_RESPONSE)
    else:
        print(f"Connection failed with code {rc}")


#接收到的消息
def on_message(client, userdata, message):
    global switch_status
    # msg = message.payload.decode()
    msg = cipher.decrypt_and_validate_message(message.payload)  # 60 seconds allowed time window
    command = msg.split()  # 拆分msg
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    # 打印接收到的消息
    #print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

    #绑定消息
    if message.topic == "bind/request":

        if command[1] == "switch":
            if command[2] == str(ssid):
                binded = True
                #发布消息：绑定成功，灯状态
                # client.publish(TOPIC_BIND_RESPONSE, f"Switch bind to {ssid} successful！")
                # client.publish(TOPIC_SWITCH_STATUS, switch_status)
                # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                encrypted_response = cipher.encrypt_message(f"Switch bind to {ssid} successful！", timestamp)
                client.publish(TOPIC_BIND_RESPONSE, encrypted_response)
                encrypted_status = cipher.encrypt_message(switch_status, timestamp)
                client.publish(TOPIC_SWITCH_STATUS, encrypted_status)
                print(f"Switch bind to {ssid} successful！")
            else:
                print("Bind switch error!")

    #控制消息
    if message.topic == "switch1/command":
        if command[0] == "on":
            switch_status = "on"
            print("Switch turned on")
            # client.publish(TOPIC_SWITCH_STATUS, switch_status)
            encrypted_status = cipher.encrypt_message(switch_status, timestamp)
            client.publish(TOPIC_SWITCH_STATUS, encrypted_status)
        elif command[0] == "off":
            switch_status = "off"
            print("Switch turned off")
            # client.publish(TOPIC_SWITCH_STATUS, switch_status)
            encrypted_status = cipher.encrypt_message(switch_status, timestamp)
            client.publish(TOPIC_SWITCH_STATUS, encrypted_status)


client.on_connect = on_connect
client.on_message = on_message

#连接MQTT服务器
client.connect(BROKER, PORT, 60)
client.loop_forever()

