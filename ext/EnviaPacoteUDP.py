#!/usr/bin/python2

from scapy.all import *

#dest = input("Destination: ")
dest = raw_input("\nDestination: ")
destport = input("Destination port: ") #Porta de destino

ip = IP(dst=dest)

udp = UDP(dport=int(destport))

pkt = ip/udp

t = sr(pkt)
#sr(pkt)
print(t)
