from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.icmp import icmp
import pox.lib.packet as pkt


import json




log = core.getLogger()

#Tabela de IP para o multicast
table_multicast = []

#Tabela dos Switches para o Multicast
tabela_switches_multicast = []
#Retorna o mac do Swtich
def dpid_to_mac (dpid):
  return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))


def _handle_PacketIn(event):
	dpid   = event.dpid
	inport = event.port
	packet = event.parsed
	handle_IP_packet(packet)

	net = packet.next # Camada de rede
	transp = packet.next.next # Camada de Transporte

	if not packet.parsed:
		return
	#if dpid not in self.arpTable:

	if packet.type == ethernet.LLDP_TYPE:
		#ignore
		return
	if isinstance(packet.next,ipv4):
        log.info('Estou aqui agora!!!')
    """
        if str(net.dstip) == "10.0.0.1":
            try:
                s1_json = open('switches/s1.json','r')
                dados_json = json.load(s1_json)
                if dados_json['id'] == 's1':
                    log.info("deu certo!!!")
            except Exception as erro:
                log.info("Ocorreu um erro ao carregar o arquivo")
                log.info("O erro eh: {}".format(erro))
    """
'''
		#verificaOrigemPacote(event)
		#Realizar os procedimentos aqui
		#log.debug("%i %i IP %s => %s", dpid, inport,packet.next.srcip, packet.next.dstip)
		#if net.protocol == 6:
			#log.info("net.dstip %s, transp.dstport %s",net.dstip,transp.dstport)
			#log.info("net.srcip %s, transp.srcport %s",net.srcip,transp.srcport)
		#if str(net.dstip) == "10.0.0.1" and transp.dstport == 80:

        
		if transp.dstport == 80: ##Aqui aplica o filtro na porta para o multicast
			log.info("---------------------")
			log.info("Filtro na porta 80")
			log.info('Src:'+str(net.srcip)+' Dst:'+str(net.dstip))
			log.info(" ")
			elem = {str(packet.src):str(net.srcip)}
			if elem not in table_multicast:
				table_multicast.append(elem)
			log.info(table_multicast)
			log.info(len(table_multicast))
			elem_switch = {dpid_to_mac(dpid):dpid}
			if elem_switch not in tabela_switches_multicast:
				tabela_switches_multicast.append(elem_switch)
			log.info(tabela_switches_multicast)
			log.info(len(tabela_switches_multicast))
			log.info("---------------------")
    '''
elif isinstance(packet.next,arp):
#log.info("Pacote ARP")
return
else:
#log.info("Sem Filtro")
return

############################################

# msg = of.ofp_flow_mod()
# msg.match.dl_src = EthAddr("00:00:00:00:00:01")
# msg.match.dl_type = 0x800

# # msg.match.nw_proto = 17

# msg.match.nw_dst = IPAddr("10.0.0.3")

# event.connection.send(msg)

# log.info("firewall reativo ativado no Switch: %s", dpidToStr(event.dpid))
def handle_IP_packet (packet):
    ip = packet.find('ipv4')
    if ip is None:
        return
        '''
	log.info(str(packet))
	log.info(str(packet.next))
	log.info(str(packet.next.next))
	log.info("Cheguuuueeeeeiiii aqui!!")
	log.info("Source IP: "+str(ip.srcip))
	'''
'''
def verificaOrigemPacote(event):
	packet = event.parsed
	net = packet.next
	transp = net.next
	#Se a origem for o servidor multicast
	if str(net.srcip) == "10.0.0.1": # Falta filtrar a porta
		if len(table_multicast) == 0:
			log.info("Multicast vazio")
		else:
			log.info(table_multicast)

'''
def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
