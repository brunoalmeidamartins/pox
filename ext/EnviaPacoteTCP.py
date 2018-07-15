from scapy.all import *

ip = IP(dst="192.168.0.1")

tcp= TCP(dport=80)

pkt = ip/udp

t = sr(pkt)

print(t)
