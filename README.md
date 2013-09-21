# Automated creation of virtual network based on real network

This [project](https://github.com/basavesh/gsoc13/wiki) will collect topology information from Controllers (for real networks) and converts the info to a Mininet custom topo file. Through which u can emulate your real network and experiment with it.

### Features
* Supports Floodlight controller and POX controller
* It assumes that one Host will have only one interface.

![Flowchart](https://lh6.googleusercontent.com/-PqZHINLoI68/Uj1aYneOkQI/AAAAAAAAAV8/BX0_Zvbny4w/s576/GSoC%2520project%2520-%2520New%2520Page%2520%25285%2529.png)

## For Floodlight Controller
* A [script](https://github.com/basavesh/gsoc13/blob/master/Floodlight_topo.py) is used to collect information from Floodlight controller via REST API
* Install python requests module from [here](http://docs.python-requests.org/en/latest/)
* Complete walk through is [here](https://github.com/basavesh/gsoc13/wiki/Walk-through-using-Floodlight-controller)

## For POX Controller
* For now works only with carp branch
* A [module](https://github.com/basavesh/gsoc13/blob/master/TestTopology.py) is used to collect informatin from POX controller via Event raisers. Download the module to your ext folder.
* Complete walk through is [here](https://github.com/basavesh/gsoc13/wiki/Walk-through-using-POX-controller)

