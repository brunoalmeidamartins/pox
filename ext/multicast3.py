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
#from scapy.all import * #Biblioteca de manipulacao de pacotes
import time
import os
import json

senha = 'bruno270591'
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
    def executaComandosOVS(self,comando): #Executa comandos direto no openvswitch
        #print(comando)
        text = os.popen("echo %s | sudo -S %s" % (senha, comando))

    def open_arquivoIPServidores(self,path):
        lista = []
        try:
            arq = open(path,'r')
            texto = arq.readlines()
            for i in texto:
                t = i.split(" ")
                lista.append(t[0])
            arq.close()
        except Exception as erro:
            log.info("Erro ao abrir arquibo"+str(erro))
        lista = sorted(set(lista))
        return lista

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
            log.info("Pacote IPv4")
            #log.info("Evento gerado na porta ="+str(inport))
            if (inport == 1 or inport == 2):
                if(net.protocol != 17):
                    '''
                    Primeiro evento gerado instala a regra para todos os hosts
                    '''
                    #Chama script de execucao dos links principais
                    log.info("Regras Iniciais Instaladas")
                    log.debug("Regras Iniciais Instaladas")
                    os.system('python pox/ext/RegrasIniciais.py')
                else:
                    if (str(transp.dstport) == '1234'): #Eventos foram gerados por hosts conectados ao swtich mas nao sao udp
                        if str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:03': # Switch onde esta os servidores S3
                            msg = of.ofp_flow_mod()
                            #msg.match.dl_src = EthAddr('00:00:00:00:01:01')
                            #msg.match.dl_dst = EthAddr('00:00:00:00:03:11')
                            msg.match.dl_type = 0x800
                            msg.match.nw_src = IPAddr("10.0.0.11")
                            msg.match.nw_dst = IPAddr(str(net.dstip))
                            msg.priority = 50001 #seta uma prioridade maior para regra
                            msg.actions.append(of.ofp_action_output(port = 17)) #Nao tem ninguem conectado a essa porta
                            event.connection.send(msg)
                            log.info("Regra de Drop Adicionada!!") # Supoe que drop o pacote
                            '''
                            Adiciona o servidor de envio no arquivo IPServidoresMulticast.txt
                            '''
                            #dado = dict(str(net.dstip) = str(transp.port))# IP Servidor e porta
                            try:
                                with open("/home/bruno/pox/ext/IPServidoresMulticast.txt","a") as arquivo:
                                    log.info("IP adicionado ao arquivo:"+str(net.dstip))
                                    arquivo.write(str(net.dstip)+' \n')
                                    arquivo.close()
                            except Exception as erro:
                                log.info("Erro ao abrir arquibo"+str(erro))

                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:01': # Swithc s1
                            '''
                            Fazer as regras aqui!!
                            '''
                            log.debug("Chegou pacote do S1 para o grupo multicast")
                            lista = self.open_arquivoIPServidores("/home/bruno/pox/ext/IPServidoresMulticast.txt")
                            #log.info(lista)
                            comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                            self.executaComandosOVS(comando)

                            comando2 = 'ovs-ofctl mod-flows s1 priority=50010,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:1'
                            #comando3 = 'ovs-ofctl add-flow s1 priority=5001,dl_type=0x800,nw_src=10.0.0.11,tp_dst=1236,actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:1'
                            self.executaComandosOVS(comando2)
                            #self.executaComandosOVS(comando3)

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
            log.info("Protocolo ARP")
            return
            '''
            a = packet.next
            if a.prototype == arp.PROTO_TYPE_IP:
                if a.hwtype == arp.HW_TYPE_ETHERNET:
                    if a.protosrc !=0:
                        if a.opcode == arp.REQUEST:
                            r = arp()
                            r.hwtype = a.hwtype
                            log.info("r.hwtype = "+str(r.hwtype))
                            r.prototype = a.prototype
                            log.info("r.prototype = "+str(r.prototype))
                            r.hwlen = a.hwlen
                            log.info("r.hwlen = "+str(r.hwlen))
                            r.protolen = a.protolen
                            log.info("r.protolen = "+str(r.protolen))
                            r.opcode = arp.REPLY
                            log.info("r.opcode = "+str(r.opcode))
                            r.hwdst = a.hwsrc
                            log.info("r.hwdst = "+str(r.hwdst))
                            r.protodst = a.protosrc
                            log.info("r.protodst = "+str(r.protodst))
                            r.protosrc = a.protodst
                            log.info("r.protosrc = "+str(r.protosrc))
                            r.hwsrc = '00:00:00:00:03:15'#self.arpTable[dpid][a.protodst].mac
                            log.info('r.hwsrc = '+str(r.hwsrc))
                            e = ethernet(type=packet.type, src=self.dpid_to_mac(dpid),
                                         dst=a.hwsrc)
                            log.info('type = '+str(packet.type))
                            log.info('src = '+str(self.dpid_to_mac(dpid)))
                            log.info('dst = '+str(a.hwsrc))
                            log.info("e = "+str(e))
                            e.set_payload(r)
                            log.info('e.set_payload = '+str(e.payload))
                            log.debug("%i %i answering ARP for %s" % (dpid, inport,
                             r.protosrc))
                            msg = of.ofp_packet_out()
                            msg.data = e.pack()
                            msg.actions.append(of.ofp_action_output(port =
                                                                    of.OFPP_IN_PORT))
                            log.info('of.OFPP_IN_PORT = '+str(of.OFPP_IN_PORT))
                            msg.in_port = inport
                            log.info('inport = '+str(inport))
                            event.connection.send(msg)
                            return
                            '''
        else:
            #log.info("Aconteceu nada!!")
            return

def launch(fakeways="", arp_for_unknowns=None, wide=False):
    #core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
    core.registerNew(multicast,fakeways, arp_for_unknowns, wide)
