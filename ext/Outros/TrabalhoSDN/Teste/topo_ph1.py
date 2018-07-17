#!/usr/bin/python
# Topologia Projeto Hipermidia - Versao 3.0
# Para interromper o envio de pacotes DHCP, parar o Network Manager: $sudo stop network-manager

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from mininet.util import dumpNodeConnections
from subprocess import call
import os

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8',
		   autoStaticArp=True,
		   host=CPULimitedHost,
		   link=TCLink)

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', mac='00:00:00:00:01:01', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', mac='00:00:00:00:01:02', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', mac='00:00:00:00:02:03', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', mac='00:00:00:00:02:04', defaultRoute=None)
    
    info( '*** Add links\n')
    linkopts = dict(bw=1000,delay='5ms',loss=0,max_queue_size=10000,use_htb=True)
    net.addLink(h1, s1, 1, 1, **linkopts)
    net.addLink(h2, s1, 1, 2, **linkopts)
    net.addLink(h3, s2, 1, 1, **linkopts)
    net.addLink(h4, s2, 1, 2, **linkopts)
    net.addLink(s1, s2, 12, 11, **linkopts) #Adicionando o link que falta na topologia


    info( '\n*** Starting network\n')
    net.build()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])

    info( '\n*** Post configure switches and hosts\n')
    dumpNodeConnections(net.hosts)

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
