from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp




log = core.getLogger()

def _handle_PacketIn(event):
	dpid   = event.dpid
	inport = event.port
	packet = event.parsed

	net = packet.next # Camada de rede
	transp = packet.next.next # Camada de Transporte

	if not packet.parsed:
		return
	#if dpid not in self.arpTable:

	if packet.type == ethernet.LLDP_TYPE:
		#ignore
		return
	if isinstance(packet.next,ipv4):
		#Realizar os procedimentos aqui
		#log.debug("%i %i IP %s => %s", dpid, inport,packet.next.srcip, packet.next.dstip)
		#if net.protocol == 6:
			#log.info("net.dstip %s, transp.dstport %s",net.dstip,transp.dstport)
			#log.info("net.srcip %s, transp.srcport %s",net.srcip,transp.srcport)
		if str(net.dstip) == "10.0.0.1" and transp.dstport == 80:
			log.info("Filtro no ip 1 e na porta 80")
		else:
			log.info(str(net.protocol))
		
	elif isinstance(packet.next,arp):
		pass



    ############################################
    
    # msg = of.ofp_flow_mod()
    # msg.match.dl_src = EthAddr("00:00:00:00:00:01")
    # msg.match.dl_type = 0x800

    # # msg.match.nw_proto = 17

    # msg.match.nw_dst = IPAddr("10.0.0.3")

    # event.connection.send(msg)

    # log.info("firewall reativo ativado no Switch: %s", dpidToStr(event.dpid))
	

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
