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

mypass = "bruno270591"

def executaComandosOVS(comando):
    #print(comando)
    text = os.popen("echo %s | sudo -S %s" % (mypass, comando))

a = 'ovs-vsctl --all destroy Queue' #Destroi todas as queue
b = 'ovs-vsctl --all destroy QoS' #Destroi todas as qos

executaComandosOVS(b)
executaComandosOVS(a)

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
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', mac='00:00:00:00:01:01', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', mac='00:00:00:00:01:02', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', mac='00:00:00:00:02:03', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', mac='00:00:00:00:02:04', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', mac='00:00:00:00:04:05', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', mac='00:00:00:00:04:06', defaultRoute=None)
    srv1 = net.addHost('srv1', cls=Host, ip='10.0.0.11', mac='00:00:00:00:03:11', defaultRoute=None)
    srv2 = net.addHost('srv2', cls=Host, ip='10.0.0.12', mac='00:00:00:00:03:12', defaultRoute=None)

    info( '*** Add links\n')
    linkopts = dict(bw=1000,delay='5ms',loss=0,max_queue_size=10000,use_htb=True)
    net.addLink(h1, s1, 1, 1, **linkopts)
    net.addLink(h2, s1, 1, 2, **linkopts)
    net.addLink(h3, s2, 1, 1, **linkopts)
    net.addLink(h4, s2, 1, 2, **linkopts)
    net.addLink(h5, s4, 1, 1, **linkopts)
    net.addLink(h6, s4, 1, 2, **linkopts)
    net.addLink(srv1, s3, 1, 1, **linkopts)
    net.addLink(srv2, s3, 1, 2, **linkopts)
    net.addLink(s1, s3, 13, 11, **linkopts)
    net.addLink(s1, s4, 14, 11, **linkopts)
    net.addLink(s2, s3, 13, 12, **linkopts)
    net.addLink(s2, s4, 14, 12, **linkopts)
    net.addLink(s3, s4, 14, 13, **linkopts)
    net.addLink(s1, s2, 12, 11, **linkopts) #Adicionando o link que falta na topologia


    info( '\n*** Starting network\n')
    net.build()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s4').start([c0])

    info( '\n*** Post configure switches and hosts\n')
    dumpNodeConnections(net.hosts)

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
