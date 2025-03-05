from datetime import datetime

import paho.mqtt.client as mqtt
import cipher
# MQTT settings
BROKER = "127.0.0.1"
PORT = 1883
TOPIC_LIGHT_STATUS = "light1/status"
TOPIC_LIGHT_COMMAND = "light1/command"
TOPIC_BIND_REQUEST = "bind/request"
TOPIC_BIND_RESPONSE = "bind/response"
ssid = 1

# Initialize switch status
light_status = "off"
binded = False

# Create client instance
client = mqtt.Client()


#连接
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(TOPIC_LIGHT_STATUS)
        client.subscribe(TOPIC_LIGHT_COMMAND)
        client.subscribe(TOPIC_BIND_REQUEST)
        client.subscribe(TOPIC_BIND_RESPONSE)
    else:
        print(f"Connection failed with code {rc}")


#接收到的消息
def on_message(client, userdata, message):
    global light_status
    # msg = message.payload.decode()
    msg = cipher.decrypt_and_validate_message(message.payload)  # 60 seconds allowed time window
    command = msg.split()  # 拆分msg
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    # 打印接收到的消息
    #print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

    #绑定消息
    if message.topic == "bind/request":

        if command[1] == "light":
            if command[2] == str(ssid):
                binded = True
                #发布消息：绑定成功，灯状态
                # client.publish(TOPIC_BIND_RESPONSE, f"Light bind to {ssid} successful！")
                # client.publish(TOPIC_LIGHT_STATUS, light_status)
                encrypted_response = cipher.encrypt_message(f"Light bind to {ssid} successful！", timestamp)
                client.publish(TOPIC_BIND_RESPONSE, encrypted_response)

                encrypted_status = cipher.encrypt_message(light_status, timestamp)
                client.publish(TOPIC_LIGHT_STATUS, encrypted_status)
                print(f"Light bind to {ssid} successful！")
            else:
                print("Bind light error!")

    #控制消息
    if message.topic == "light1/command":
        if command[0] == "on":
            light_status = "on"
            print("Light turned on")
            # client.publish(TOPIC_LIGHT_STATUS, light_status)
            encrypted_status = cipher.encrypt_message(light_status, timestamp)
            client.publish(TOPIC_LIGHT_STATUS, encrypted_status)

        elif command[0] == "off":
            light_status = "off"
            print("Light turned off")
            # client.publish(TOPIC_LIGHT_STATUS, light_status)
            encrypted_status = cipher.encrypt_message(light_status, timestamp)
            client.publish(TOPIC_LIGHT_STATUS, encrypted_status)


client.on_connect = on_connect
client.on_message = on_message

#连接MQTT服务器
client.connect(BROKER, PORT, 60)
client.loop_forever()

