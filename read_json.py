
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


import getopt, sys
import json

def main():
	'''
	converts the json formatted topology information into custom mininet topo file.
	'''
	try:
		opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["input=", "output="])
	except getopt.GetoptError as err:
		print str(err) # will print something like "option -a not recognized"
		sys.exit(2)
	outfile = 'output.py'
	infile = 'jsondata.txt'
	for o, a in opts:
            
		if o in ("-i", "--input"):
			infile = a
		elif o in ("-o", "--output"):
			outfile = a
		else:
			assert False, "unhandled option"
    
	ifh = open(infile,'r')
	ofh = open(outfile,'w')

	data = json.load(ifh)
	
	# creating mininet file 
	ofh.write("from mininet.topo import Topo\n\n")
	ofh.write("class MyTopo( Topo ):\n")
	ofh.write("\t'Trying to create a Mininet File'\n")

	ofh.write("\n\tdef __init__( self ):\n")


	ofh.write("\n\t\tTopo.__init__( self )\n")
	ofh.write("\t\t# Initialize topology\n\n")

	# commands to add hosts
	ofh.write("\t\t# Add hosts\n")
	for host in data['hosts']:
		if data['hosts'][host]['IP'] is None:
			
			ofh.write("\t\t{} = self.addHost('{}', mac = '{}')\n".format(data['hosts'][host]['name'],data['hosts'][host]['name'], host))

		else:
			ofh.write("\t\t{} = self.addHost('{}', ip = '{}', mac = '{}' )\n".format(data['hosts'][host]['name'],data['hosts'][host]['name'], data['hosts'][host]['IP'], host))
			

	ofh.write("\n")

	# commands to add switches
	ofh.write("\t\t# Add switches\n")
	for switch in data['switches']:
		ofh.write("\t\t{} = self.addSwitch('{}')\n".format(data['switches'][switch]['name'],data['switches'][switch]['name']))

	# commands to add links between switches
	ofh.write("\n\t\t# Add links\n")
	for link in data['links']:
		ofh.write("\t\tself.addLink( {}, {}, {}, {} )\n".format(data['switches'][link.split(' ')[0]]['name'],data['switches'][link.split(' ')[1]]['name'], data['links'][link]['src_port'], data['links'][link]['dst_port'] ))

	# commands to add links between switch and hosts
	ofh.write("\n\n")
	for host in data['hosts']:
		ofh.write("\t\tself.addLink( {}, {}, 1, {} )\n".format(data['hosts'][host]['name'], data['switches'][data['hosts'][host]['to_switch']]['name'], data['hosts'][host]['to_port']))


	ofh.write("\n\ntopos = { 'mytopo': ( lambda: MyTopo() ) }")
	ofh.close()
	ifh.close()

if __name__ == "__main__":
    main()



