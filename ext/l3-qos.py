# Copyright 2012-2013 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modulo l3_learning com aplicacao de QoS - Versao 7.0

"""
A stupid L3 switch

For each switch:
1) Keep a table that maps IP addresses to MAC addresses and switch ports.
   Stock this table using information from ARP and IP packets.
2) When you see an ARP query, try to answer it using information in the table
   from step 1.  If the info in the table is old, just flood the query.
3) Flood all other ARPs.
4) When you see an IP packet, if you know the destination port (because it's
   in the table from step 1), install a flow for it.
"""

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
import pickle

# Timeout for flows
FLOW_IDLE_TIMEOUT = 30  # IDLE_TIMEOUT alterado de 10 para 30

# Timeout for ARP entries
ARP_TIMEOUT = 60 * 2

# Maximum number of packet to buffer on a switch for an unknown IP
MAX_BUFFERED_PER_IP = 5

# Maximum time to hang on to a buffer for an unknown IP in seconds
MAX_BUFFER_TIME = 5

# Porta do servidor
SERVER_PORT = 23000

# Porta do modulo RSVP Client
RSVP_CLIENT_PORT = 23231

# Porta do modulo RSVP Server
RSVP_SERVER_PORT = 23232

# Vazao maxima da rede (bps)
TX_MAX = 10000000

# Arquivo e variaveis de lista de objetos Classe
filename = '/home/atavares/pox/ext/classes.conf'
global classlist
global be


class Entry (object):
  """
  Not strictly an ARP entry.
  We use the port to determine which port to forward traffic out of.
  We use the MAC to answer ARP replies.
  We use the timeout so that if an entry is older than ARP_TIMEOUT, we
   flood the ARP request rather than try to answer it ourselves.
  """

  def __init__(self, port, mac):
    self.timeout = time.time() + ARP_TIMEOUT
    self.port = port
    self.mac = mac

  def __eq__(self, other):
    if type(other) == tuple:
      return (self.port, self.mac) == other
    else:
      return (self.port, self.mac) == (other.port, other.mac)

  def __ne__(self, other):
    return not self.__eq__(other)

  def isExpired(self):
    if self.port == of.OFPP_NONE:
      return False
    return time.time() > self.timeout


def dpid_to_mac(dpid):
  return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))

# Carregamento da lista de objetos Classe


def loadClass():
  global classlist
  global be
  if os.path.isfile(filename):
    filec = open(filename, 'rb')
    classlist = pickle.load(filec)
    filec.close()
    be = classlist[0].pico


class l3_switch (EventMixin):
  def __init__(self, fakeways=[], arp_for_unknowns=False):
    # These are "fake gateways" -- we'll answer ARPs for them with MAC
    # of the switch they're connected to.
    self.fakeways = set(fakeways)

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
    self._expire_timer = Timer(5, self._handle_expiration, recurring=True)

    self.listenTo(core)

    # Inclusao de dicionario de mapeamento de IP, porta e fila de QoS
    self.portMap = {}

    # Inclusao de dicionario de registro de disponibilidade de QoS em cada enlace de cada switch
    self.hasQoS = {}

  def _handle_expiration(self):
    # Called by a timer so that we can remove old items.
    empty = []
    for k, v in self.lost_buffers.iteritems():
      dpid, ip = k

      for item in list(v):
        expires_at, buffer_id, in_port = item
        if expires_at < time.time():
          # This packet is old.  Tell this switch to drop it.
          v.remove(item)
          po = of.ofp_packet_out(buffer_id=buffer_id, in_port=in_port)
          core.openflow.sendToDPID(dpid, po)
      if len(v) == 0:
        empty.append(k)

    # Remove empty buffer bins
    for k in empty:
      del self.lost_buffers[k]

  def _send_lost_buffers(self, dpid, ipaddr, macaddr, port):
    """
    We may have "lost" buffers -- packets we got but didn't know
    where to send at the time.  We may know now.  Try and see.
    """
    if (dpid, ipaddr) in self.lost_buffers:
      # Yup!
      bucket = self.lost_buffers[(dpid, ipaddr)]
      del self.lost_buffers[(dpid, ipaddr)]
      log.debug("Sending %i buffered packets to %s from %s"
                % (len(bucket), ipaddr, dpid_to_str(dpid)))
      for _, buffer_id, in_port in bucket:
        po = of.ofp_packet_out(buffer_id=buffer_id, in_port=in_port)
        po.actions.append(of.ofp_action_dl_addr.set_dst(macaddr))
        po.actions.append(of.ofp_action_output(port=port))
        core.openflow.sendToDPID(dpid, po)

  def _handle_GoingUpEvent(self, event):
    self.listenTo(core.openflow)
    log.info("Up...")
    # Chama a funcao de carregamento de lista de objetos Classe
    loadClass()
    log.info("Carregada lista de classes de servico...")

  def _handle_PacketIn(self, event):
    dpid = event.connection.dpid
    inport = event.port
    packet = event.parsed

    if not packet.parsed:
      log.warning("%i %i ignoring unparsed packet", dpid, inport)
      return

    if dpid not in self.arpTable:
      # New switch -- create an empty table
      self.arpTable[dpid] = {}
      # Cria uma tabela vazia para registro de disponibilidade de QoS
      self.hasQoS[dpid] = {}
      for fake in self.fakeways:
        self.arpTable[dpid][IPAddr(fake)] = Entry(of.OFPP_NONE,
                                                  dpid_to_mac(dpid))

    if packet.type == ethernet.LLDP_TYPE:
      # Ignore LLDP packets
      return

    if isinstance(packet.next, ipv4):
      log.debug("%i %i IP %s => %s", dpid, inport,
                packet.next.srcip, packet.next.dstip)

      # Send any waiting packets...
      self._send_lost_buffers(dpid, packet.next.srcip, packet.src, inport)

      # Learn or update port/MAC info
      if packet.next.srcip in self.arpTable[dpid]:
        if self.arpTable[dpid][packet.next.srcip] != (inport, packet.src):
          log.info("%i %i RE-learned %s", dpid, inport, packet.next.srcip)
      else:
        log.debug("%i %i learned %s", dpid, inport, str(packet.next.srcip))
      self.arpTable[dpid][packet.next.srcip] = Entry(inport, packet.src)

      # Try to forward
      dstaddr = packet.next.dstip
      if dstaddr in self.arpTable[dpid]:
        # We have info about what port to send it out on...

        prt = self.arpTable[dpid][dstaddr].port
        mac = self.arpTable[dpid][dstaddr].mac
        if prt == inport:
          log.warning("%i %i not sending packet for %s back out of the " +
                      "input port" % (dpid, inport, str(dstaddr)))
        else:
          log.debug("%i %i installing flow for %s => %s out port %i"
                    % (dpid, inport, packet.next.srcip, dstaddr, prt))

          actions = []
          actions.append(of.ofp_action_dl_addr.set_dst(mac))
          actions.append(of.ofp_action_output(port=prt))
          match = of.ofp_match.from_packet(packet, inport)
          match.dl_src = None  # Wildcard source MAC

          msg = of.ofp_flow_mod(command=of.OFPFC_ADD,
                                idle_timeout=FLOW_IDLE_TIMEOUT,
                                hard_timeout=of.OFP_FLOW_PERMANENT,
                                buffer_id=event.ofp.buffer_id,
                                actions=actions,
                                match=of.ofp_match.from_packet(packet,
                                                               inport))
          event.connection.send(msg.pack())

        ##########################################################################################################
        ########################################### Instrucoes QoS ###############################################
        ##########################################################################################################
        net = packet.next
        transp = packet.next.next

        # Realiza o mapeamento inicial entre IP, porta e QoS (-1)
        if net.protocol == 6 and transp.dstport == SERVER_PORT:
          if not self.portMap.has_key(net.srcip):
            self.portMap = {net.srcip: (transp.srcport, -1)}

        # Testa se o pacote eh UDP (troca de mensagens RSVP)
        if net.protocol == 17:
          # Testa se a mensagem eh RSVP originada pelo cliente
          if transp.srcport == RSVP_CLIENT_PORT:
            # Testa se a mensagem eh RSVP RESV
            if net.tos != 0:
              # Atualiza a fila do mapeamento IP, porta e QoS
              port, queue = self.portMap[net.srcip]
              queue = (net.tos / 10) - 1
              self.portMap[net.srcip] = (port, queue)
              # Consulta a disponibilidade de QoS na porta de saida do roteador
              if not self.hasQoS[dpid].has_key(inport):
                self.hasQoS[dpid][inport] = be
              if self.hasQoS[dpid][inport] + classlist[queue].pico <= TX_MAX:
                log.info("QoS disponivel em R%d - porta %d: %d", dpid,
                         inport, TX_MAX - self.hasQoS[dpid][inport])
              else:
                log.info("QoS nao disponivel - largura de banda insuficiente")
            # Testa de a mensagem eh RSVP FIN
            else:
              # Exclui o mapeamento IP, porta e QoS
              if self.portMap.has_key(net.srcip):
                del self.portMap[net.srcip]

          # Testa se a mensagem eh RSVP originada pelo servidor
          if transp.srcport == RSVP_SERVER_PORT:
            # Testa se a mensagem eh RSVP RESV_CONF
            if net.tos != 0:
              port, queue = self.portMap[net.dstip]
              # Aplica QoS na porta de saida do roteador
              qos = os.popen(
                  "ovs-vsctl list qos | grep _uuid | awk '{print $3}'").read().strip('\n')
              os.system('ovs-vsctl set port r%d-eth%d qos=%s' %
                        (dpid, prt, qos))
              log.info("QoS %s aplicada em R%s - porta %d", qos, dpid, prt)
              # Acrescenta a banda alocada a tabela de disponibilidade de QoS
              self.hasQoS[dpid][prt] += classlist[self.portMap[net.dstip][1]].pico
              # Copia os parametros de cabecalho do pacote UDP
              msg1 = of.ofp_flow_mod(command=of.OFPFC_MODIFY)
              msg1.match = of.ofp_match.from_packet(packet, inport)
              # Altera os parametros de cabecalho para o futuro fluxo TCP
              msg1.priority = 65535
              msg1.idle_timeout = 30
              msg1.hard_timeout = 120
              msg1.match.nw_proto = 6
              msg1.match.nw_tos = 0
              msg1.match.tp_src = SERVER_PORT
              msg1.match.tp_dst = port
              msg1.actions.append(
                  of.ofp_action_enqueue(port=prt, queue_id=queue))
              # Instala a regra no roteador
              event.connection.send(msg1)
              log.info("Fila %d aplicada ao fluxo tp_dst %d", queue, port)

        ##########################################################################################################
        ########################################### Instrucoes QoS ###############################################
        ##########################################################################################################

      elif self.arp_for_unknowns:
        # We don't know this destination.
        # First, we track this buffer so that we can try to resend it later
        # if we learn the destination, second we ARP for the destination,
        # which should ultimately result in it responding and us learning
        # where it is

        # Add to tracked buffers
        if (dpid, dstaddr) not in self.lost_buffers:
          self.lost_buffers[(dpid, dstaddr)] = []
        bucket = self.lost_buffers[(dpid, dstaddr)]
        entry = (time.time() + MAX_BUFFER_TIME, event.ofp.buffer_id, inport)
        bucket.append(entry)
        while len(bucket) > MAX_BUFFERED_PER_IP:
          del bucket[0]

        # Expire things from our outstanding ARP list...
        self.outstanding_arps = {k: v for k, v in
                                 self.outstanding_arps.iteritems() if v > time.time()}

        # Check if we've already ARPed recently
        if (dpid, dstaddr) in self.outstanding_arps:
          # Oop, we've already done this one recently.
          return

        # And ARP...
        self.outstanding_arps[(dpid, dstaddr)] = time.time() + 4

        r = arp()
        r.hwtype = r.HW_TYPE_ETHERNET
        r.prototype = r.PROTO_TYPE_IP
        r.hwlen = 6
        r.protolen = r.protolen
        r.opcode = r.REQUEST
        r.hwdst = ETHER_BROADCAST
        r.protodst = dstaddr
        r.hwsrc = packet.src
        r.protosrc = packet.next.srcip
        e = ethernet(type=ethernet.ARP_TYPE, src=packet.src,
                     dst=ETHER_BROADCAST)
        e.set_payload(r)
        log.debug("%i %i ARPing for %s on behalf of %s" % (dpid, inport,
                                                           str(r.protodst), str(r.protosrc)))
        msg = of.ofp_packet_out()
        msg.data = e.pack()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.in_port = inport
        event.connection.send(msg)

    elif isinstance(packet.next, arp):
      a = packet.next
      log.debug("%i %i ARP %s %s => %s", dpid, inport,
                {arp.REQUEST: "request", arp.REPLY: "reply"}.get(a.opcode,
                                                                 'op:%i' % (a.opcode,)), str(a.protosrc), str(a.protodst))

      if a.prototype == arp.PROTO_TYPE_IP:
        if a.hwtype == arp.HW_TYPE_ETHERNET:
          if a.protosrc != 0:

            # Learn or update port/MAC info
            if a.protosrc in self.arpTable[dpid]:
              if self.arpTable[dpid][a.protosrc] != (inport, packet.src):
                log.info("%i %i RE-learned %s", dpid, inport, str(a.protosrc))
            else:
              log.debug("%i %i learned %s", dpid, inport, str(a.protosrc))
            self.arpTable[dpid][a.protosrc] = Entry(inport, packet.src)

            # Send any waiting packets...
            self._send_lost_buffers(dpid, a.protosrc, packet.src, inport)

            if a.opcode == arp.REQUEST:
              # Maybe we can answer

              if a.protodst in self.arpTable[dpid]:
                # We have an answer...

                if not self.arpTable[dpid][a.protodst].isExpired():
                  # .. and it's relatively current, so we'll reply ourselves

                  r = arp()
                  r.hwtype = a.hwtype
                  r.prototype = a.prototype
                  r.hwlen = a.hwlen
                  r.protolen = a.protolen
                  r.opcode = arp.REPLY
                  r.hwdst = a.hwsrc
                  r.protodst = a.protosrc
                  r.protosrc = a.protodst
                  r.hwsrc = self.arpTable[dpid][a.protodst].mac
                  e = ethernet(type=packet.type, src=dpid_to_mac(dpid),
                               dst=a.hwsrc)
                  e.set_payload(r)
                  log.debug("%i %i answering ARP for %s" % (dpid, inport,
                                                            str(r.protosrc)))
                  msg = of.ofp_packet_out()
                  msg.data = e.pack()
                  msg.actions.append(
                      of.ofp_action_output(port=of.OFPP_IN_PORT))
                  msg.in_port = inport
                  event.connection.send(msg)
                  return

      # Didn't know how to answer or otherwise handle this ARP, so just flood it
      log.debug("%i %i flooding ARP %s %s => %s" % (dpid, inport,
                                                    {arp.REQUEST: "request", arp.REPLY: "reply"}.get(a.opcode,
                                                                                                     'op:%i' % (a.opcode,)), str(a.protosrc), str(a.protodst)))

      msg = of.ofp_packet_out(in_port=inport, data=event.ofp,
                              action=of.ofp_action_output(port=of.OFPP_FLOOD))
      event.connection.send(msg)


def launch(fakeways="", arp_for_unknowns=None):
  fakeways = fakeways.replace(",", " ").split()
  fakeways = [IPAddr(x) for x in fakeways]
  if arp_for_unknowns is None:
    arp_for_unknowns = len(fakeways) > 0
  else:
    arp_for_unknowns = str_to_bool(arp_for_unknowns)
  core.registerNew(l3_switch, fakeways, arp_for_unknowns)