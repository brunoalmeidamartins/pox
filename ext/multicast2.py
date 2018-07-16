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

senha = 'Pass'
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


      #Tabela de ARP de IPServidores
      self.arpTableServidores = {'10.0.0.18':'00:00:00:00:03:18',
                              '10.0.0.19':'00:00:00:00:03:19',
                              '10.0.0.20':'00:00:00:00:03:20'}

      #Tabela de servidores Multicast
      self.tableIPServidores = []

      #Tabela de swtichs que contem o fluxo de determinado IP
      self.tableSwtichFluxo = {'00:00:00:00:00:01':[],
                               '00:00:00:00:00:02':[],
                               '00:00:00:00:00:03':[],
                               '00:00:00:00:00:04':[]}

      # This timer handles expiring stuff
      #self._expire_timer = Timer(5, self._handle_expiration, recurring=True)


      core.listen_to_dependencies(self)
    #Funcao retorna uma string com portas do switch com o fluxo
    def retornaStringListaPortas(self,dpid_switch,ip_fluxo):
        l = self.tableSwtichFluxo[dpid_switch]
        k = {}
        for i in l:
            for j in i:
                if str(j) == str(ip_fluxo):
                    k = i
        #log.info(k)
        lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
        u = lista_portas
        p = ''
        t = 0
        for i in u:
            if t == 0:
                p = p +str(i)
            else:
                p = p +','+ str(i)
            t = t+1
        #log.info(p)
        return p
    # Funcao que retorna o switch e a porta de um host a partir de um endereco IP
    def getSwitchPort(self,ip):
        self.hosts = core.host_tracker.entryByMAC
        for h in self.hosts.keys():
            ip_aux = self.hosts[h].ipAddrs.keys()[0]
            if ip_aux == ip:
                return (self.hosts[h].dpid,self.hosts[h].port)
    #Funcao que envia um ARP Reply
    def sendARP(self,a,portaSaida, dpid_switch,tipo_pkt,event):
        #s,p = self.getSwitchPort(a.protodst)
        s = dpid_switch
        #s = 1
        log.info('dpid_switch = '+str(s))
        p = portaSaida
        log.info('Porta said = '+str(p))
        e = ethernet(type=tipo_pkt,src=a.hwsrc,dst=a.hwdst)
        e.payload = a
        #log.info('Switch %d answering ARP_REPLY for %s to port %s' %(s,str(a.protosrc),p))
        msg = of.ofp_packet_out()
        #msg = of.ofp_action_nw_addr()
        #log.debug(of.ofp_packet_out())
        msg.data = e.pack()
        #msg.match.dl_type = 0x800
        #log.info("msg.nw_src = "+str(msg.protodst))
        log.debug(dir(msg))
        #log.info(msg._buffer_id)
        #msg.nw_src = IPAddr("10.0.0.18")
        #msg.nw_dst = IPAddr("10.0.0.1")
        msg.actions.append(of.ofp_action_output(port=p))
        msg.actions.append(of.ofp_action_dl_addr.set_src(EthAddr('00:00:00:00:03:18')))
        msg.actions.append(of.ofp_action_dl_addr.set_dst(EthAddr('00:00:00:00:01:01')))
        msg.actions.append(of.ofp_action_nw_addr.set_src(IPAddr("10.0.0.18")))
        msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr("10.0.0.1")))
        log.info(msg.show())
        log.debug(msg.actions)
        #core.openflow.getConnection(s).send(msg)
        event.connection.send(msg)

    # Funcao que cria um ARP_REPLY a partir de um MAC conhecido
    def replyARP(self,a,mac):
        r = pkt.arp()
        r.hwtype = a.hwtype
        r.prototype = a.prototype
        r.hwlen = a.hwlen
        r.protolen = a.protolen
        r.opcode = pkt.arp.REPLY
        r.hwdst = a.hwsrc
        r.hwsrc = mac
        r.protodst = a.protosrc
        r.protosrc = a.protodst
        e = pkt.ethernet(type=packet.type,dst=a.hwsrc)
        e.payload = r
        log.info('Switch %d answering ARP_REPLY for %s to port %s' %(event.dpid,str(a.protodst),event.port))
        msg = of.ofp_packet_out()
        msg.data = e.pack()
        msg.actions.append(of.ofp_action_output(port=event.port))
        event.connection.send(msg)
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
                #if()
                lista = []
                for i in self.arpTableServidores:
                    lista.append(i)

                #if(net.protocol != 17):
                if str(net.dstip) not in lista:
                    '''
                    Primeiro evento gerado instala a regra para todos os hosts
                    '''
                    #Chama script de execucao dos links principais
                    log.debug("Regras Iniciais Instaladas")
                    os.system('python pox/ext/RegrasIniciais.py')
                else:
                    #if (str(transp.dstport) == '1234'): #Eventos foram gerados por hosts conectados ao swtich
                    if str(net.dstip) in lista:
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

                            #dado = dict(str(net.dstip) = str(transp.port))# IP Servidor e porta
                            try:
                                with open("/home/bruno/pox/ext/IPServidoresMulticast.txt","a") as arquivo:
                                    log.info("IP adicionado ao arquivo:"+str(net.dstip))
                                    arquivo.write(str(net.dstip)+' \n')
                                    arquivo.close()
                            except Exception as erro:
                                log.info("Erro ao abrir arquivo"+str(erro))
                            '''
                            '''
                            Adiciona o IP do servidor multicast a tabela
                            '''
                            lista_Portas = []
                            if str(net.dstip) not in self.tableIPServidores:
                                self.tableIPServidores.append(str(net.dstip))
                                lista_Portas = [17]
                                info = {str(net.dstip):lista_Portas}
                                self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                            else:
                                log.info("IP Servidor ja registrado!!")
                            return

                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:01': # Swithc s1
                            '''
                            Fazer as regras aqui!!
                            '''
                            log.debug("Chegou pacote do S1 para o grupo multicast")
                            #Verificar se o swtich ja possui o fluxo requerido
                            l = self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))]
                            k = {}
                            for i in l:
                                for j in i:
                                    if str(j) == str(net.dstip):
                                        k = i
                            if len(k) != 0:
                                #Levar o fluxo para a porta entao
                                log.debug('Switch ja possui o Fluxo')
                                p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.2,mod_dl_dst:00:00:00:00:01:02,output:'+p+',1'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [1]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:'+p+',2'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [2]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                return
                            else:
                                log.debug('Switch ainda nao possui o Fluxo')
                                #Trazer o fluxo para o switch
                                #comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                                #comando = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                                #self.executaComandosOVS(comando)
                                #p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip)
                                p = self.retornaStringListaPortas('00:00:00:00:00:03',net.dstip) #Lista de portas que contem o fluxo
                                comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:'+p+',11'
                                self.executaComandosOVS(comando)


                                l = self.tableSwtichFluxo['00:00:00:00:00:03']
                                k = {}
                                for i in l:
                                    for j in i:
                                        if str(j) == str(net.dstip):
                                            k = i
                                #log.info(k)
                                lista_portas = k[str(net.dstip)] #lista de portas que estao com fluxo swtich
                                lista_portas.append(11) #Porta que vai para o S1



                                #Verifico de qual porta veio para fazer a rescrita de cabecalho
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=5001,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:1'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [1]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=5001,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.2,mod_dl_dst:00:00:00:00:01:02,output:2'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [2]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                return



                            #comando2 = 'ovs-ofctl mod-flows s1 priority=50010,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:1'
                            #comando3 = 'ovs-ofctl add-flow s1 priority=5001,dl_type=0x800,nw_src=10.0.0.11,tp_dst=1236,actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:1'
                            #self.executaComandosOVS(comando2)
                            #self.executaComandosOVS(comando3)




                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:02': #Switch s2
                            '''
                            Fazer as regras aqui!!
                            '''
                            log.debug("Chegou pacote do S2 para o grupo multicast")
                            #Verificar se o swtich ja possui o fluxo requerido
                            l = self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))]
                            k = {}
                            for i in l:
                                for j in i:
                                    if str(j) == str(net.dstip):
                                        k = i
                            if len(k) != 0:
                                log.debug('Switch ja possui o Fluxo')
                                #Levar o fluxo para a porta entao
                                p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.4,mod_dl_dst:00:00:00:00:02:04,output:'+p+',1'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [1]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:02:03,output:'+p+',2'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [2]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                return
                            else:
                                log.debug('Switch ainda nao possui o Fluxo')
                                #Trazer o fluxo para o switch
                                #comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                                #comando = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                                #self.executaComandosOVS(comando)
                                #p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip)
                                p = self.retornaStringListaPortas('00:00:00:00:00:03',net.dstip) #Lista de portas que contem o fluxo
                                comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:'+p+',12'
                                self.executaComandosOVS(comando)


                                l = self.tableSwtichFluxo['00:00:00:00:00:03']
                                k = {}
                                for i in l:
                                    for j in i:
                                        if str(j) == str(net.dstip):
                                            k = i
                                #log.info(k)
                                lista_portas = k[str(net.dstip)] #lista de portas que estao com fluxo swtich
                                lista_portas.append(12) #Porta que vai para o S2



                                #Verifico de qual porta veio para fazer a rescrita de cabecalho
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:02:03,output:1'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [1]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.4,mod_dl_dst:00:00:00:00:02:04,output:2'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [2]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                return




                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:04': #Swtich s4
                            '''
                            Fazer as regras aqui!!
                            '''
                            log.debug("Chegou pacote do S4 para o grupo multicast")
                            #Verificar se o swtich ja possui o fluxo requerido
                            l = self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))]
                            k = {}
                            for i in l:
                                for j in i:
                                    if str(j) == str(net.dstip):
                                        k = i
                            if len(k) != 0:
                                log.debug('Switch ja possui o Fluxo')
                                #Levar o fluxo para a porta entao
                                p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.6,mod_dl_dst:00:00:00:00:04:06,output:'+p+',1'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [1]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:04:05,output:'+p+',2'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [2]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                return
                            else:
                                log.debug('Switch ainda nao possui o Fluxo')
                                #Trazer o fluxo para o switch
                                #comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                                #comando = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:11'
                                #self.executaComandosOVS(comando)
                                #p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip)
                                p = self.retornaStringListaPortas('00:00:00:00:00:03',net.dstip) #Lista de portas que contem o fluxo
                                comando = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:'+p+',14'
                                self.executaComandosOVS(comando)


                                l = self.tableSwtichFluxo['00:00:00:00:00:03']
                                k = {}
                                for i in l:
                                    for j in i:
                                        if str(j) == str(net.dstip):
                                            k = i
                                #log.info(k)
                                lista_portas = k[str(net.dstip)] #lista de portas que estao com fluxo swtich
                                lista_portas.append(14) #Porta que vai para o S4



                                #Verifico de qual porta veio para fazer a rescrita de cabecalho
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.5,mod_dl_dst:00:00:00:00:04:05,output:1'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [1]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.6,mod_dl_dst:00:00:00:00:04:06,output:2'
                                    self.executaComandosOVS(comando2)
                                    lista_Portas = [2]
                                    info = {str(net.dstip):lista_Portas}
                                    self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))].append(info) #Adiciona o IP e a porta que ele esta saido na tabela de Fluxo do Switch
                                return

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
            a = packet.find('arp')
            mac = self.arpTableServidores[str(net.protodst)]
            r = arp()
            r.hwtype = a.hwtype
            r.prototype = a.prototype
            r.hwlen = a.hwlen
            r.protolen = a.protolen
            r.opcode = arp.REPLY
            r.hwdst = a.hwsrc
            r.hwsrc = mac
            r.protodst = a.protosrc
            r.protosrc = a.protodst
            self.sendARP(r, inport, event.dpid, packet.type, event)
            return
            '''
            '''
            packet1 = event.parsed
            if packet.payload.opcode == arp.REQUEST:
                r = arp()
                r.hwsrc = self.arpTableServidores[str(net.protodst)]
                r.hwdst = packet1.src
                r.opcode = arp.REPLY
                r.protosrc = IPAddr(str(net.protodst))
                r.protodst = IPAddr(str(packet1.next.protosrc))
                ether = ethernet()
                ether.type = ethernet.ARP_TYPE
                ether.dst = packet1.src
                ether.src = self.arpTableServidores[str(net.protodst)]
                ether.payload = r
                #envia pacote
                msg3 = of.ofp_packet_out()
                msg3.data = ether.pack()
                msg3.actions.append(of.ofp_action_output(port =
                                                        of.OFPP_IN_PORT))
                #log.info('of.OFPP_IN_PORT = '+str(of.OFPP_IN_PORT))
                msg3.in_port = inport
                #log.info('inport = '+str(inport))
                event.connection.send(msg3)
                return
            elif packet.payload.opcode == arp.REPLY:
                return
            else:
                return
            '''


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
    #def start():
        #core.registerNew(multicast,fakeways, arp_for_unknowns, wide)
        #log.info('Multicast3')
    #core.call_when_ready(start,['openflow_discovery','host_tracker','Traffic'])
    #core.call_when_ready(start,['host_tracker'])
    #if core._waiters:
        #log.warning('Missing component... Shut down POX')
        #core.quit()
