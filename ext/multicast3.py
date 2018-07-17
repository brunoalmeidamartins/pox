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
#import pox.host_tracker.host_tracker as host_tracker #Biblioteca host_tracker
import pox.proto.arp_helper as arp_helper
#from scapy.all import * #Biblioteca de manipulacao de pacotes
import time
import os
import json

mypass = 'bruno270591'
#Instala as regras inicais nos swtiches
def _handle_ConnectionUp(event):
    '''
    Primeiro evento gerado pelo swtich s3 instala as regras iniciais
    '''
    dpid = event.dpid
    if str(dpid)== '3': #Instala as regras Iniciais
        #Chama script de execucao dos links principais
        log.debug("Regras Iniciais Instaladas")
        os.system('python pox/ext/RegrasIniciais.py')
        log.debug("Regras de Qos Instaladas")
        os.system('python pox/ext/CriaQoS.py')


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
                              '10.0.0.20':'00:00:00:00:03:20',
                              '10.0.0.21':'00:00:00:00:03:21',
                              '10.0.0.22':'00:00:00:00:03:22',
                              '10.0.0.23':'00:00:00:00:03:23'}

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

    def executaComandosOVS(self,comando): #Executa comandos direto no openvswitch
        #print(comando)
        text = os.popen("echo %s | sudo -S %s" % (mypass, comando))

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
            #log.info("Pacote IPv4")
            #log.info("Evento gerado na porta ="+str(inport))
            if (inport == 1 or inport == 2):
                #if()
                lista = []
                for i in self.arpTableServidores:
                    lista.append(i)

                if str(net.dstip) not in lista:
                    #Faz nada
                    return
                else:
                    #if (str(transp.dstport) == '1234'): #Eventos foram gerados por hosts conectados ao swtich
                    if str(net.dstip) in lista and str(transp.dstport) != '12320':
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
                            a = []
                            if len(k) != 0:
                                a = k[str(net.dstip)] #lista de portas que estao com fluxo swtich
                            if len(a) != 0:
                                #Levar o fluxo para a porta entao
                                log.debug('Switch ja possui o Fluxo')
                                p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.2,mod_dl_dst:00:00:00:00:01:02,output:'+p+',1'
                                    self.executaComandosOVS(comando2)
                                    a.append(1)
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:'+p+',2'
                                    self.executaComandosOVS(comando2)
                                    a.append(2)
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
                            a = []
                            if len(k) != 0:
                                a = k[str(net.dstip)] #lista de portas que estao com fluxo swtich
                            if len(a) != 0:
                                log.debug('Switch ja possui o Fluxo')
                                #Levar o fluxo para a porta entao
                                p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.4,mod_dl_dst:00:00:00:00:02:04,output:'+p+',1'
                                    self.executaComandosOVS(comando2)
                                    a.append(1)
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:02:03,output:'+p+',2'
                                    self.executaComandosOVS(comando2)
                                    a.append(2)
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
                            a = []
                            if len(k) != 0:
                                a = k[str(net.dstip)] #lista de portas que estao com fluxo swtich
                            if len(a) != 0:
                                log.debug('Switch ja possui o Fluxo')
                                #Levar o fluxo para a porta entao
                                p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                if inport == 1:
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.6,mod_dl_dst:00:00:00:00:04:06,output:'+p+',1'
                                    self.executaComandosOVS(comando2)
                                    a.append(1)
                                else:
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=50002,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:04:05,output:'+p+',2'
                                    self.executaComandosOVS(comando2)
                                    a.append(2)
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
                    else: #Pedido para sair do Grupo Multicast
                        '''
                        Pedido para sair do Grupo Multicast
                        '''
                        log.info('IP = '+str(net.srcip)+' quer sair do Grupo Multicast '+str(net.dstip))

                        ip_fluxo = net.dstip
                        l = self.tableSwtichFluxo[str(self.dpid_to_mac(dpid))]
                        k = {}
                        for i in l:
                            for j in i:
                                if str(j) == str(ip_fluxo):
                                    k = i
                        #log.info(k)
                        t = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                        log.debug(t)


                        if str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:01': # Swithc s1
                            '''
                            Fazer as regras aqui!!
                            '''
                            p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                            if len(t) == 1: #Tem somente um fluno no switch
                                #Retiro o fluxo da porta em s3
                                l = self.tableSwtichFluxo['00:00:00:00:00:03']
                                k = {}
                                for i in l:
                                    for j in i:
                                        if str(j) == str(ip_fluxo):
                                            k = i
                                #log.info(k)
                                lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                lista_portas.remove(11)
                                b = self.retornaStringListaPortas('00:00:00:00:00:03',net.dstip) #Lista de portas que contem o fluxo
                                comando2 = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:'+b
                                self.executaComandosOVS(comando2)
                                del t[:] #Apaga lista de portas do fluxo no swtich

                            else:
                                #Retiro somente o fluxo da porta
                                if inport == 1:
                                    l = self.tableSwtichFluxo['00:00:00:00:00:01']
                                    k = {}
                                    for i in l:
                                        for j in i:
                                            if str(j) == str(ip_fluxo):
                                                k = i
                                    #log.info(k)
                                    lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                    lista_portas.remove(1)
                                    b = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:02,output:'+b
                                    #comando2 = 'ovs-ofctl mod-flows s1 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b
                                    log.debug(comando2)
                                    self.executaComandosOVS(comando2)
                                else:
                                    l = self.tableSwtichFluxo['00:00:00:00:00:01']
                                    k = {}
                                    for i in l:
                                        for j in i:
                                            if str(j) == str(ip_fluxo):
                                                k = i
                                    #log.info(k)
                                    lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                    lista_portas.remove(2)
                                    b = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                    comando2 = 'ovs-ofctl mod-flows s1 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.1,mod_dl_dst:00:00:00:00:01:01,output:'+b
                                    #comando2 = 'ovs-ofctl mod-flows s1 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b
                                    log.debug(comando2)
                                    self.executaComandosOVS(comando2)
                                return
                            return
                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:02': # Swithc s2
                            '''
                            Fazer as regras aqui!!
                            '''
                            p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                            if len(t) == 1: #Tem somente um fluno no switch
                                #Retiro o fluxo da porta em s3
                                l = self.tableSwtichFluxo['00:00:00:00:00:03']
                                k = {}
                                for i in l:
                                    for j in i:
                                        if str(j) == str(ip_fluxo):
                                            k = i
                                #log.info(k)
                                lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                lista_portas.remove(12)
                                b = self.retornaStringListaPortas('00:00:00:00:00:03',net.dstip) #Lista de portas que contem o fluxo
                                comando2 = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:'+b
                                self.executaComandosOVS(comando2)
                                del t[:] #Apaga lista de portas do fluxo no swtich
                            else:
                                #Retiro somente o fluxo da porta
                                if inport == 1:
                                    l = self.tableSwtichFluxo['00:00:00:00:00:02']
                                    k = {}
                                    for i in l:
                                        for j in i:
                                            if str(j) == str(ip_fluxo):
                                                k = i
                                    #log.info(k)
                                    lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                    lista_portas.remove(1)
                                    b = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.4,mod_dl_dst:00:00:00:00:02:04,output:'+b
                                    #comando2 = 'ovs-ofctl mod-flows s2 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b
                                    self.executaComandosOVS(comando2)
                                else:
                                    l = self.tableSwtichFluxo['00:00:00:00:00:02']
                                    k = {}
                                    for i in l:
                                        for j in i:
                                            if str(j) == str(ip_fluxo):
                                                k = i
                                    #log.info(k)
                                    lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                    lista_portas.remove(2)
                                    b = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                    comando2 = 'ovs-ofctl mod-flows s2 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:02:03,output:'+b
                                    #comando2 = 'ovs-ofctl mod-flows s2 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b
                                    self.executaComandosOVS(comando2)
                                return
                            return
                        elif str(self.dpid_to_mac(dpid)) == '00:00:00:00:00:04': # Swithc s4
                            '''
                            Fazer as regras aqui!!
                            '''
                            p = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                            if len(t) == 1: #Tem somente um fluno no switch
                                #Retiro o fluxo da porta em s3
                                l = self.tableSwtichFluxo['00:00:00:00:00:03']
                                k = {}
                                for i in l:
                                    for j in i:
                                        if str(j) == str(ip_fluxo):
                                            k = i
                                #log.info(k)
                                lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                lista_portas.remove(14)
                                b = self.retornaStringListaPortas('00:00:00:00:00:03',net.dstip) #Lista de portas que contem o fluxo
                                comando2 = 'ovs-ofctl mod-flows s3 priority=5001,dl_type=0x800,nw_src=10.0.0.11,nw_dst='+str(net.dstip)+',actions=output:'+b
                                #comando2 = 'ovs-ofctl mod-flows s3 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b
                                self.executaComandosOVS(comando2)
                                del t[:] #Apaga lista de portas do fluxo no swtich
                            else:
                                #Retiro somente o fluxo da porta
                                if inport == 1:
                                    l = self.tableSwtichFluxo['00:00:00:00:00:04']
                                    k = {}
                                    for i in l:
                                        for j in i:
                                            if str(j) == str(ip_fluxo):
                                                k = i
                                    #log.info(k)
                                    lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                    lista_portas.remove(1)
                                    b = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.6,mod_dl_dst:00:00:00:00:04:06,output:'+b
                                    #comando2 = 'ovs-ofctl mod-flows s4 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b
                                    self.executaComandosOVS(comando2)
                                else:
                                    l = self.tableSwtichFluxo['00:00:00:00:00:04']
                                    k = {}
                                    for i in l:
                                        for j in i:
                                            if str(j) == str(ip_fluxo):
                                                k = i
                                    #log.info(k)
                                    lista_portas = k[str(ip_fluxo)] #lista de portas que estao com fluxo swtich
                                    lista_portas.remove(2)
                                    b = self.retornaStringListaPortas(str(self.dpid_to_mac(dpid)),net.dstip) #Lista de portas que contem o fluxo
                                    comando2 = 'ovs-ofctl mod-flows s4 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=mod_nw_dst:10.0.0.5,mod_dl_dst:00:00:00:00:04:05,output:'+b
                                    #comando2 = 'ovs-ofctl mod-flows s4 priority=49999,dl_type=0x800,nw_dst='+str(net.dstip)+',actions=output:'+b

                                    self.executaComandosOVS(comando2)
                                return

                            return
                        else:
                            return
                        return

        elif isinstance(net,arp):
            log.info("Protocolo ARP")
            mac_resp =  self.arpTableServidores[str(net.protodst)]
            arp_helper.send_arp_reply(event,mac_resp)
            return
        else:
            #log.info("Aconteceu nada!!")
            return

def launch(fakeways="", arp_for_unknowns=None, wide=False):
    core.registerNew(multicast,fakeways, arp_for_unknowns, wide)
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
