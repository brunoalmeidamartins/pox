from pox.core import core
import pox
log = core.getLogger()
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import str_to_bool, dpid_to_str
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
import time
import os
import json

class multicast (EventMixin):
#class multicast (object):
    def __init__ (self, fakeways = [], arp_for_unknowns = False, wide = False):
      # These are "fake gateways" -- we'll answer ARPs for them with MAC
      # of the switch they're connected to.
      self.fakeways = set(fakeways)

      # If True, we create "wide" matches.  Otherwise, we create "narrow"
      # (exact) matches.
      self.wide = wide

      # If this is true and we see a packet for an unknown
      # host, we'll ARP for it.
      self.arp_for_unknowns = arp_for_unknowns

      # (dpid,IP) -> expire_time
      # We use this to keep from spamming ARPs
      self.outstanding_arps = {}

      # (dpid,IP) -> [(expire_time,buffer_id,in_port), ...]
      # These are buffers we've gotten at this datapath for this IP which
      # we can't deliver because we don't know where they go.
      self.lost_buffers = {}

      # For each switch, we map IP addresses to Entries
      self.arpTable = {}

      # This timer handles expiring stuff
      #self._expire_timer = Timer(5, self._handle_expiration, recurring=True)


      core.listen_to_dependencies(self)


    def dpid_to_mac (self,dpid):
        return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))


    def defineSaidaHost(self, EnderecoMac, porta):
        msg = of.ofp_flow_mod()
        msg.match.dl_dst = EthAddr(EnderecoMac)
        msg.actions.append(of.ofp_action_output(port = porta))
        return msg
    def _handle_openflow_PacketIn (self, event):
    #def _handle_PacketIn (self, event):
        dpid = event.dpid
        inport = event.port
        packet = event.parsed
        #log.info('Pacote de '+ str(self.dpid_to_mac(dpid)))

        net = packet.next # Camada de rede
        transp = packet.next.next # Camada de transporte

        if not packet.parsed:
            log.info("Pacote not Parsed")
            return
        #if packet.type == ethernet.LLDPTYPE:
            #.info("Pacote LLDPTYPE")
            #return
        if isinstance(net, ipv4):
            #log.info("Pacote IPv4")
            #log.info("Evento gerado na porta ="+str(inport))
            if (inport == 1 or inport == 2):
                if(net.protocol != 17):
                    '''
                    Primeiro evento gerado instala a regra para todos os hosts
                    '''
                    #Chama script de execucao dos links principais
                    log.info("Regras Iniciais Instaladas")
                    os.system('python pox/ext/RegrasIniciais.py')
                else:
                    if (str(transp.dstport) == '1234'): #Eventos foram gerados por hosts conectados ao swtich mas nao sao udp
                        if str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:03': # Switch onde esta os servidores S3
                            msg = of.ofp_flow_mod()
                            #msg.match.dl_src = EthAddr('00:00:00:00:01:01')
                            #msg.match.dl_dst = EthAddr('00:00:00:00:03:11')
                            msg.priority = 50001 #seta uma prioridade maior para regra
                            msg.actions.append(of.ofp_action_output(port = 17)) #Nao tem ninguem conectado a essa porta
                            event.connection.send(msg)
                            log.info("Regra de Drop Adicionada!!") # Supoe que drop o pacote
                            '''
                            Adiciona o servidor de envio no arquivo IPServidoresMulticast.json
                            '''
                            dado = dict(str(net.dstip) = str(transp.port))# IP Servidor e porta
                            try:
                                arquivo_json = open("IPServidoresMulticast.json","w")
                                arquivo_json.write(dado)
                                arquivo_json.close()

                            except Exception as erro:
                                log.info("Erro ao abrir arquibo"+erro)


                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:01': # Swithc s1
                            '''
                            Fazer as regras aqui!!
                            '''
                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:02': #Switch s2
                            '''
                            Fazer as regras aqui!!
                            '''
                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:04': #Swtich s3
                            '''
                            Fazer as regras aqui!!
                            '''
            '''
            if str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:01':
                #(inport == 1)
                msg = of.ofp_flow_mod()
                msg.match.dl_src = EthAddr('00:00:00:00:01:01')
                msg.match.dl_dst = EthAddr('00:00:00:00:03:11')
                msg.actions.append(of.ofp_action_output(port = 13))
                event.connection.send(msg)

                #msg2 = of.ofp_flow_mod()
                #msg2.match.dl_dst = EthAddr('00:00:00:00:01:01')
                #msg2.actions.append(of.ofp_action_output(port = 1))
                #event.connection.send(self.defineSaidaHost('00:00:00:00:01:01',1))
                #log.info(msg)
            elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:03':
                msg = of.ofp_flow_mod()
                msg.match.dl_src = EthAddr('00:00:00:00:03:11')
                msg.match.dl_dst = EthAddr('00:00:00:00:01:01')
                msg.actions.append(of.ofp_action_output(port = 11))
                event.connection.send(msg)

                #msg2 = of.ofp_flow_mod()
                #msg2.match.dl_dst = EthAddr('00:00:00:00:03:11')
                #msg2.actions.append(of.ofp_action_output(port = 1))
                event.connection.send(self.defineSaidaHost('00:00:00:00:03:11',1))
                #log.info(msg)
            '''
        elif isinstance(net,arp):
            log.info("Pacote ARP")
            log.info(net)
            log.info(" ")
            return
        else:
            #log.info("Aconteceu nada!!")
            return

def launch(fakeways="", arp_for_unknowns=None, wide=False):
    #core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
    core.registerNew(multicast,fakeways, arp_for_unknowns, wide)
