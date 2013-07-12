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


		

topology = MyTopology() # Created an empty instance of Mytopology 


##### Fetch data From Controller using REST API ############################

######################## get list of all switches ##########################
try:
	command = 'curl -s http://'+controllerIP+ \
	          ':'+cport+'/wm/core/controller/switches/json'

except Exception:
	print "make sure that the controller is running"
	sys.exit()

data  = os.popen(command).read()
switches = json.loads(data)

for i in range(len(switches)):
	switch_dpid = switches[i]['dpid']
	topology.add_switch(switch_dpid)

print "\nSwitches are: "
for switch in topology.switches:
	print switch

#################################end #######################################

####################### get list of end devices ############################
command = 'curl -s http://'+controllerIP+ ':'+cport+'/wm/device/'
data  = os.popen(command).read()
hosts = json.loads(data)
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
	print "MAC: {}".format(host)
	print "IP: {}".format(topology.hosts[host]['IP'])
	print "to_switch: {}".format(topology.hosts[host]['to_switch'])
	print "to_port: {}".format(topology.hosts[host]['to_port'])
	print "\n"

#for host in topology.hosts:
#	print host	
################################end ########################################


################## get list of links #######################################
command = 'curl -s http://'+controllerIP+ ':'+cport+'/wm/topology/links/json'
data  = os.popen(command).read()
links = json.loads(data)

for i in range(len(links)):
	src_switch = links[i]['src-switch']
	dst_switch = links[i]['dst-switch']
	src_port = links[i]['src-port']
	dst_port = links[i]['dst-port']
	topology.add_link(src_switch, src_port, dst_switch, dst_port)

for link in topology.links:
	print "{} --> {} {}".format(link[0],link[1],topology.links[link])
############################# end ##########################################

