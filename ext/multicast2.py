from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.icmp import icmp
import pox.lib.packet as pkt

log = core.getLogger()

def dpid_to_mac (dpid):
    return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))

def _handle_PacketIn(event):
    dpid = event.dpid
    inport = event.port
    packet = event.parsed
    log.info('Pacote de '+ str(dpid_to_mac(dpid)))

    net = packet.next # Camada de rede
    transp = packet.next.next # Camada de transporte

    if not packet.parsed:
        log.info("Pacote not Parsed")
        return
    #if packet.type == ethernet.LLDPTYPE:
        #.info("Pacote LLDPTYPE")
        #return
    if isinstance(net, ipv4):
        log.info("Pacote IPv4")
        #log.info("Estou aqui!!")
        if str(dpid_to_mac(dpid)) == '00:00:00:00:00:01':
            msg = of.ofp_flow_mod()
            msg.match.dl_src = EthAddr('00:00:00:00:01:01')
            msg.match.dl_dst = EthAddr('00:00:00:00:03:11')
            msg.actions.append(of.ofp_action_output(port = 13))
            event.connection.send(msg)

            msg2 = of.ofp_flow_mod()
            msg2.match.dl_dst = EthAddr('00:00:00:00:01:01')
            msg2.actions.append(of.ofp_action_output(port = 1))
            event.connection.send(msg2)
            #log.info(msg)
        elif str(dpid_to_mac(dpid)) == '00:00:00:00:00:03':
            msg = of.ofp_flow_mod()
            msg.match.dl_src = EthAddr('00:00:00:00:03:11')
            msg.match.dl_dst = EthAddr('00:00:00:00:01:01')
            msg.actions.append(of.ofp_action_output(port = 11))
            event.connection.send(msg)

            msg2 = of.ofp_flow_mod()
            msg2.match.dl_dst = EthAddr('00:00:00:00:03:11')
            msg2.actions.append(of.ofp_action_output(port = 1))
            event.connection.send(msg2)
            #log.info(msg)

    elif isinstance(net,arp):
        log.info("Pacote ARP")
        return
    else:
        #log.info("Aconteceu nada!!")
        return

def launch():
    core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
