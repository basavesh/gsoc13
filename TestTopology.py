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

import json
import os, sys
import getopt
from threading import Timer
from time import sleep
from pox.lib.recoco import Timer


log = core.getLogger()

outfile = 'jsondata.txt'

stop_condition = False
data = {}

		
class MyTopology (object):
	'''
	MyTopology class stores the topology information
	1. Switch: dpid
	2. hosts: MAC + IP (should do pingall) + Switch's dpid and port no to which it is connected
	3. link: stores info of a link between two switches
	'''
	def __init__(self):

		#core.listen_to_dependencies(self)
		self.switches = {}
		self.hosts = {}
		self.links = {}
		self.host_counter = 0
		self.host_counter = 0
		self.switch_counter = 0


	def add_host(self,MAC, IP = None, to_switch = None, to_port = None):

		self.hosts[MAC] = {}
		self.hosts[MAC]['IP'] = IP
		self.hosts[MAC]['to_switch'] = to_switch
		self.hosts[MAC]['to_port'] = to_port

		self.host_counter += 1
		self.hosts[MAC]['name'] = 'h{}'.format(self.host_counter)


	def update_host(self, MAC, IP = None, to_switch = None, to_port = None):
		
		self.hosts[MAC]['IP'] = IP
		self.hosts[MAC]['to_switch'] = to_switch
		self.hosts[MAC]['to_port'] = to_port


	def update_IP(self, MAC, IP):

		self.hosts[MAC]['IP'] = IP


	def  del_host(self, MAC):
		del self.hosts[MAC]


	def add_switch(self, dpid):
		self.switch_counter += 1

		self.switches[dpid] = {}
		self.switches[dpid]['name'] = 's{}'.format(self.switch_counter)


	def del_switch(self, dpid):

		del self.switches[dpid]		


	def add_link(self, dpid1, port1, dpid2, port2):
	
		if str(dpid2) + ' ' + str(dpid1) not in self.links:

			link =  str(dpid1) + ' ' + str(dpid2)

			self.links[link] = {}
			self.links[link]['src_port'] = port1
			self.links[link]['dst_port'] = port2
		

	def del_link(self, dpid1, dpid2):

		if str(dpid1) + ' ' + str(dpid2) in self.links:

			del self.links[str(dpid1) + ' ' + str(dpid2)]

topology = MyTopology()

class TestTopology(object):


	def __init__(self):
		core.listen_to_dependencies(self)
		

	def _handle_host_tracker_HostEvent(self, event):
		'''
		Used to manage Host and its properties
		'''

		if event.join == True:
			topology.add_host(str(event.entry.macaddr),None,str(event.entry.dpid),event.entry.port)

		elif event.move == True:
			topology.update_host(str(event.entry.macaddr),None,str(event.entry.dpid),event.entry.port)	

		elif event.leave == True:
			topology.del_host(str(event.entry.macaddr))


	def _handle_openflow_discovery_LinkEvent(self, event):
		'''
		Used to manage list of switches and links between switches
		'''
		if event.added == True:
			
			if event.link.dpid1 not in topology.switches:
				topology.add_switch(event.link.dpid1)

			if event.link.dpid2 not in topology.switches:
				topology.add_switch(event.link.dpid2)

			topology.add_link(event.link.dpid1, event.link.port1, event.link.dpid2, event.link.port2)

		if event.removed == True:

			if event.link.dpid1 in topology.switches:
				topology.del_switch(event.link.dpid1)

			if event.link.dpid2 in topology.switches:
				topology.del_switch(event.link.dpid2)

			topology.del_link(event.link.dpid1, event.link.dpid2)
			

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
				topology.update_IP(str(packet.src), str(packet.next.protosrc))


def update_file ():
	if stop_condition: return False

	data['switches'] = topology.switches

	data['hosts'] = topology.hosts
	data['links'] = topology.links

	f = open(outfile,'w')
	json.dump(data, f)
	f.close()

  	print "Updated {} file".format(outfile)




def launch(**kw):

	core.registerNew(TestTopology)
	Timer(30, update_file, recurring = True)




