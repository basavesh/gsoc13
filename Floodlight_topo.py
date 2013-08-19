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
This script collects Topology information from Floodlight controller 
using REST API

Execute this python script in the machine where Floodlight is running
or change the controllerIP and port accordingly

'''

import os 				# OS Calls
import sys 				# System Calls
import json				# To convert to and fro from json to python objects
import struct 
import requests

controllerIP = 'localhost'		 # 
cport = '8080'


class MyTopology (object):
	'''
	MyTopology class stores the topology information
	1. Switch: dpid
	2. hosts: MAC + IP (should do pingall) + Switch's dpid and port no to which it is connected
	3. link: stores info of a link between two switches
	'''
	def __init__(self):

		self.switches = {}
		self.hosts = {}
		self.links = {}
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
	
		if (dpid2,dpid1) not in self.links:
			self.links[(dpid1,dpid2)] = {}
			self.links[(dpid1,dpid2)]['src_port'] = port1
			self.links[(dpid1,dpid2)]['dst_port'] = port2
		

	def del_link(self, dpid1, dpid2):

		del self.links[(dpid1,dpid2)]


		

topology = MyTopology() # Created an empty instance of Mytopology 


##### Fetch data From Controller using REST API ############################

######################## get list of all switches ##########################
try:
	command = 'http://'+controllerIP+ \
	          ':'+cport+'/wm/core/controller/switches/json'

except Exception:
	print "make sure that the controller is running"
	sys.exit()

r = requests.get(command)
switches = json.loads(r.content)

for i in range(len(switches)):
	switch_dpid = switches[i]['dpid']
	topology.add_switch(switch_dpid)

print "\nSwitches are: "
for switch in topology.switches:
	
	print topology.switches[switch]['name'], switch

#################################end #######################################

####################### get list of end devices ############################
command = 'http://'+controllerIP+ ':'+cport+'/wm/device/'
r = requests.get(command)
hosts = json.loads(r.content)
for i in range(len(hosts)):
	if len(hosts[i]['attachmentPoint']) > 0:
		
		#ipv4 = hosts[i]['ipv4'][0]
		mac = hosts[i]['mac'][0]
		to_switch = hosts[i]['attachmentPoint'][0]['switchDPID']
		to_port = hosts[i]['attachmentPoint'][0]['port']

		topology.add_host(mac, None, to_switch, to_port)

		try:
			if hosts[i]['ipv4'][0]:
				topology.update_IP(mac,hosts[i]['ipv4'][0])

		except Exception :
			pass
				
print "\nHosts are: "
for host in topology.hosts:
	print "Name: {}".format(topology.hosts[host]['name'])
	print "MAC: {}".format(host)
	print "IP: {}".format(topology.hosts[host]['IP'])
	print "to_switch: {}".format(topology.hosts[host]['to_switch'])
	print "to_port: {}".format(topology.hosts[host]['to_port'])
	print "\n"

#for host in topology.hosts:
#	print host	
################################end ########################################


################## get list of links #######################################
command = 'http://'+controllerIP+ ':'+cport+'/wm/topology/links/json'
r = requests.get(command)
links = json.loads(r.content)

for i in range(len(links)):
	src_switch = links[i]['src-switch']
	dst_switch = links[i]['dst-switch']
	src_port = links[i]['src-port']
	dst_port = links[i]['dst-port']
	topology.add_link(src_switch, src_port, dst_switch, dst_port)

for link in topology.links:
	print "{} --> {} {}".format(link[0],link[1],topology.links[link])
############################# end ##########################################





# try to create a simple mininet topo file

f = open('test.py', 'w')

f.write("from mininet.topo import Topo\n\n")
f.write("class MyTopo( Topo ):\n")
f.write("\t'Trying to create a Mininet File'\n")

f.write("\n\tdef __init__( self ):\n")


f.write("\n\t\tTopo.__init__( self )\n")
f.write("\t\t# Initialize topology\n\n")

f.write("\t\t# Add hosts\n")
for host in topology.hosts:
	if topology.hosts[host]['name'] is None:
		f.write("\t\t{} = self.addHost('{}', mac = '{}')\n".format(topology.hosts[host]['name'],topology.hosts[host]['name'], host))

	else:
		f.write("\t\t{} = self.addHost('{}', ip = '{}', mac = '{}' )\n".format(topology.hosts[host]['name'],topology.hosts[host]['name'], topology.hosts[host]['IP'], host))


f.write("\n")

f.write("\t\t# Add switches\n")
for switch in topology.switches:
	f.write("\t\t{} = self.addSwitch('{}')\n".format(topology.switches[switch]['name'],topology.switches[switch]['name']))

f.write("\n\t\t# Add links\n")
for link in topology.links:
	f.write("\t\tself.addLink( {}, {}, {}, {} )\n".format(topology.switches[link[0]]['name'],topology.switches[link[1]]['name'], topology.links[link]['src_port'], topology.links[link]['dst_port'] ))

f.write("\n\n")
for host in topology.hosts:
	f.write("\t\tself.addLink( {}, {}, 1, {} )\n".format(topology.hosts[host]['name'], topology.switches[topology.hosts[host]['to_switch']]['name'], topology.hosts[host]['to_port']))


f.write("\n\ntopos = { 'mytopo': ( lambda: MyTopo() ) }")
f.close()

