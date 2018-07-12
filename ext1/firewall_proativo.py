from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

def (event):

	msg = of.ofp_flow_mod()
	msg.match.dl_type = 0x800

	msg.match.nw_proto = 17

	msg.match.nw_dst = IPAddr("10.0.0.3")

	event.connection.send(msg)

	log.info("firewall proativo no Switch: %s",dpidToStr(event.dpid))

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectioUp)
	log.info("firewall_proativo activado.")

