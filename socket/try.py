import socket
from binascii import unhexlify
import time

host="192.168.1.3"
port=102


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

s.send(unhexlify('0300001611e00000000100c1020101c2020101c0010a'))
time.sleep(1)

s.send(unhexlify('0300001902f08032010000ccc100080000f0000001000103c0'))
time.sleep(1)

s.send(unhexlify('0300002102f0803201000000050010000029000000000009505f50524f4752414d'))
time.sleep(10)



s.close()