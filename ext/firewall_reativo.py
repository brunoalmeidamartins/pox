from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()


def _handle_PacketIn(event):
    msg = of.ofp_flow_mod()
    msg.match.dl_src = EthAddr("00:00:00:00:01")
    msg.match.dl_type = 0x800

    #msg.match.nw_proto = 17

    msg.match.nw_dst = IPAddr("10.0.0.3")

    event.connection.send(msg)

    log.info("firewall reativo ativado no Switch: %s", dpidToStr(event.dpid))


def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("firewall_reativo ativado.")
