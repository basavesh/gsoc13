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
import requests			# Used to access REST API
import pickle
import getopt




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
		'''
		Function to add host
		'''

		self.hosts[MAC] = {}
		self.hosts[MAC]['IP'] = IP
		self.hosts[MAC]['to_switch'] = to_switch
		self.hosts[MAC]['to_port'] = to_port

		self.host_counter += 1
		self.hosts[MAC]['name'] = 'h{}'.format(self.host_counter)


	def update_host(self, MAC, IP = None, to_switch = None, to_port = None):
		'''
		Function to update host when host moves from one switch to another or If it's IP address is updated or changed
		'''
		self.hosts[MAC]['IP'] = IP
		self.hosts[MAC]['to_switch'] = to_switch
		self.hosts[MAC]['to_port'] = to_port


	def update_IP(self, MAC, IP):
		'''
		update ip of the host using MAC
		'''
		self.hosts[MAC]['IP'] = IP


	def  del_host(self, MAC):
		'''
		delete host from the topology
		'''
		del self.hosts[MAC]


	def add_switch(self, dpid):
		'''
		add switch to the topology
		'''		
		self.switch_counter += 1

		self.switches[dpid] = {}
		self.switches[dpid]['name'] = 's{}'.format(self.switch_counter) # to Identify the switch


	def del_switch(self, dpid):
		'''
		delete switch from the topology
		'''
		del self.switches[dpid]		


	def add_link(self, dpid1, port1, dpid2, port2):
		'''
		Adds link between two switches to the topology
		'''
	
		if str(dpid2) + ' ' + str(dpid1) not in self.links:

			link =  str(dpid1) + ' ' + str(dpid2)

			self.links[link] = {}
			self.links[link]['src_port'] = port1
			self.links[link]['dst_port'] = port2
		

def main(): 		

	try:
		opts, args = getopt.getopt(sys.argv[1:], "o:", ["output=","ip=","port="])
	except getopt.GetoptError as err:
		print str(err) # will print something like "option -a not recognized"
		sys.exit(2)

	outfile = 'jsondata.txt'
	controllerIP = 'localhost'	
	cport = '8080'

	# Configuring the options
	for o, a in opts:
            
		if o in ("-o", "--output"):
			outfile = a

		elif o == "--ip":
			controllerIP = a

		elif o == "--port":
			cport = a

		else:
			assert False, "unhandled option"

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


	# editted hereeeeeee --- 


	for link in topology.links:
		print "{} --> {} {}".format(link.split(' ')[0],link.split(' ')[1],topology.links[link])
	############################# end ##########################################



	############## try for json formatting ################
	data = {}
	data['switches'] = topology.switches
	data['hosts'] = topology.hosts
	data['links'] = topology.links

	f = open(outfile,'w')
	json.dump(data, f)
	f.close()


if __name__ == "__main__":
    main()