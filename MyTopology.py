# Copyright 2013 Basavesh Shivakumar
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

'''
The MyTopology module collects metadata information of topology using LinkEvent and
HostEvent event raisers of pox's carp branch.

To run this module:
use carp branch of pox and place this MyTopology file in ext folder 
execute './pox.py samples.httopo MyTopology'

NOTE: still under development
'''

from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_dpid

from pox.lib.addresses import EthAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp

from pox.lib.recoco import Timer
from pox.lib.revent import Event, EventHalt

log = core.getLogger()

		
class MyTopology (object):
	'''
	MyTopology class stores the topology information
	1. Switch: dpid
	2. hosts: MAC + IP (should do pingall) + Switch's dpid and port no to which it is connected
	3. link: stores info of a link between two switches
	'''
	def __init__(self):

		core.listen_to_dependencies(self)
		self.switches = []
		self.hosts = {}
		self.links = {}


	def add_host(self,MAC, IP = None, to_switch = None, to_port = None):

		self.hosts[MAC] = {}
		self.hosts[MAC]['IP'] = IP
		self.hosts[MAC]['to_switch'] = to_switch
		self.hosts[MAC]['to_port'] = to_port


	def update_host(self, MAC, IP = None, to_switch = None, to_port = None):
		
		self.hosts[MAC]['IP'] = IP
		self.hosts[MAC]['to_switch'] = to_switch
		self.hosts[MAC]['to_port'] = to_port


	def update_IP(self, MAC, IP):

		self.hosts[MAC]['IP'] = IP


	def  del_host(self, MAC):
		del self.hosts[MAC]


	def add_switch(self, dpid):
		
		self.switches.append(dpid)


	def del_switch(self, dpid):

		self.switches.remove(dpid)		


	def add_link(self, dpid1, port1, dpid2, port2):
	
		self.links[(dpid1,dpid2)] = {}
		self.links[(dpid1,dpid2)]['src_port'] = port1
		self.links[(dpid1,dpid2)]['dst_port'] = port2
		

	def del_link(self, dpid1, dpid2):

		del self.links[(dpid1,dpid2)]


	def _handle_host_tracker_HostEvent(self, event):
		'''
		Used to manage Host and its properties
		'''

		if event.join == True:
			self.add_host(event.entry.macaddr,None,event.entry.dpid,event.entry.port)

		elif event.move == True:
			self.update_host(event.entry.macaddr,None,event.entry.dpid,event.entry.port)	

		elif event.leave == True:
			self.del_host(event.entry.macaddr)


	def _handle_openflow_discovery_LinkEvent(self, event):
		'''
		Used to manage list of switches and links between switches
		'''
		if event.added == True:
			
			if event.link.dpid1 not in self.switches:
				self.add_switch(event.link.dpid1)

			if event.link.dpid2 not in self.switches:
				self.add_switch(event.link.dpid2)

			self.add_link(event.link.dpid1, event.link.port1, event.link.dpid2, event.link.port2)

		if event.removed == True:

			if event.link.dpid1 in self.switches:
				self.del_switch(event.link.dpid1)

			if event.link.dpid2 in self.switches:
				self.del_switch(event.link.dpid2)

			self.del_link(event.link.dpid1, event.link.dpid2)
			

	def _handle_openflow_PacketIn (self, event):
		'''
		Used to update IP address.
		'''
		packet = event.parsed

		if not packet.parsed:
			return

		if packet.type == ethernet.LLDP_TYPE:
			return

		if isinstance(packet.next, arp):
			if (packet.next.hwtype == arp.HW_TYPE_ETHERNET and packet.next.prototype == arp.PROTO_TYPE_IP and packet.next.protosrc != 0):
				self.update_IP(packet.src, packet.next.protosrc)



def launch():
	core.registerNew(MyTopology)


