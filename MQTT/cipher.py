import json
from datetime import datetime
# from crypto.Random import get_random_bytes
from cryptography.fernet import Fernet

# 生成一个密钥
# key = Fernet.generate_key()
# print(key)
# 将随机生成的密钥用作客户端之间的私钥
key=b'BaWNLI6nEvsQ3QZfEgfqgi70RVq3DGc6Jjt4YT_5a-Q='
cipher_suite = Fernet(key)#生成加密器
MAX_MESSAGE_AGE = 60#规定时间间隔

# Function to encrypt a message with a timestamp
def encrypt_message(message, timestamp):
    message_with_timestamp = {
        'message': message,
        'timestamp': timestamp
    }
    json_message = json.dumps(message_with_timestamp)
    encrypted_message = cipher_suite.encrypt(json_message.encode())
    return encrypted_message


# Function to decrypt a message and check timestamp
def decrypt_and_validate_message(encrypted_message):
    decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
    message_with_timestamp = json.loads(decrypted_message)
    timestamp = message_with_timestamp['timestamp']
    received_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    current_time = datetime.now()
    # print(received_time)
    # print(current_time)
    time_difference = abs((current_time - received_time).total_seconds())

    if time_difference <= MAX_MESSAGE_AGE:
        return message_with_timestamp['message']
    else:
        raise ValueError("Message is out of the allowed time window")