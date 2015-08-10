#!/usr/bin/python

#CS456 Assignment #3 - Router
#Justin Franchetto
#20375706
#Implements a router as outlined in the specifications
#Accepts packets from the emulator and operates on them accordingly. 

import sys, logging, os
from socket import *
from packetOps import *
from db import *

#dijkstraCompute():
#Purpose: computes and updates the router information base (RIB) 
#using Dijkstra's shortest cost path algorithm. 
def dijkstraCompute():

	#Initialize
	D = {router_id : 0}			#Current cost from source to dest		
	P = {router_id : None}			#Predeccesors
	N = [router_id]				#Set of nodes with known least cost path
	infoBase.addDest(router_id, "Local", D[router_id])

	allNodes = range(1, NBR_ROUTER()+1)
	for node in allNodes:
		if node != router_id:
			myNeighbours = topology.findNeighbours(router_id)
			if node in myNeighbours:
				D[node] = (topology.findCost(router_id, node))
				P[node] = node
				infoBase.addDest(node, P[node], D[node])
			else:
				D[node] = (float("inf"))

	#Compute shortest cost paths
	while(len(N) < NBR_ROUTER()):
		minWeight = (None, float("inf"))
		#Find node w, not in N with minimum cost D[w] and add it to N
		for node in allNodes:
			if not(node in N) and (D[node] < minWeight[1]):		
				minWeight = (node, D[node])
		N.append(minWeight[0])									

		#Loop on all of w's neighbours, updating the cost and predecessor if necessary.
		#Finally, update the RIB
		for neighbour in topology.findNeighbours(minWeight[0]):	
			if not(neighbour in N):
				D[neighbour] = min(D[neighbour], D[minWeight[0]] + topology.findCost(minWeight[0], neighbour))
				P[neighbour] = P[minWeight[0]]
				infoBase.addDest(neighbour, P[minWeight[0]], D[neighbour])

#sendDB:
#Creates LSPDUs to send our circuit DB to our neighbours
def sendDB(hellopkt):
	for neighbour in circuitDB.linkcost:
		LSPDUpkt = pkt_LSPDU(router_id, router_id, neighbour.link, neighbour.cost, hellopkt.link_id)	
		routerSocket.sendto(LSPDUpkt.toByteArray(), (nse_host, nse_port))
		log.info(LSPDUpkt.log("send", router_id))

#Parse the command line arguments
if (len(sys.argv) == 5):
	router_id = int(sys.argv[1])
	nse_host = sys.argv[2]
	nse_port = int(sys.argv[3])
	router_port = int(sys.argv[4])
else:
	print "Invalid parameters"
	quit()

#Initialize the socket for comms with the emulator
routerSocket = socket(AF_INET, SOCK_DGRAM)
routerSocket.bind(("", router_port))

#Initialize the various router DBs
topology = topDB(router_id)
infoBase = RIB(router_id, NBR_ROUTER())

#Initialize the logger
filename = "router" + str(router_id) + ".log"
if (os.path.isfile(filename)): os.remove(filename)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename)
handler.setLevel(logging.INFO)
log.addHandler(handler)

#Send init packet to the emulator
initPkt = pkt_INIT(router_id)
routerSocket.sendto(initPkt.toByteArray(), (nse_host, nse_port))
log.info(initPkt.log("send", router_id))

#Receive the circuit DB from the emulator
data, client = routerSocket.recvfrom(4096)
circuitDB = getPacket(data, True)[1]
log.info(circuitDB.log("receive", router_id))

#Send Hello to neighbours
for neighbour in circuitDB.linkcost:
	helloPkt = pkt_HELLO(router_id, neighbour.link)
	changed = topology.addLink(router_id, neighbour.link, neighbour.cost)
	#if changed: log.info(topology.printTopology())
	routerSocket.sendto(helloPkt.toByteArray(), (nse_host, nse_port))
	log.info(helloPkt.log("send", router_id))

#Receive packets and handle them depending on type
neighboursMet = list()

while(True):
	data, client = routerSocket.recvfrom(4096)
	packet = getPacket(data)
	pType = packet[0]
	pData = packet[1]
	log.info(pData.log("receive", router_id))

	if pType == "HELLO":
		#Record that we have received a hello from this neighbour
		#and send them our entire DB as LSPDU packets
		neighboursMet.append(pData.router_id)
		changed = topology.updateLink(pData.router_id, pData.link_id)
		log.info(topology.printTopology())
		log.info(infoBase.printInfoBase())
		sendDB(pData)
	elif pType == "LSPDU":
		#Try to update topology, changed is true or false
		changed = topology.addLink(pData.router_id, pData.link_id, pData.cost)

		#We updated the DB:
		#Log, forward to appropriate neighbours and use Djikstra's to compute the shortest cost path and update the RIB
		if changed:
			log.info(topology.printTopology())	
			for neighbour in neighboursMet:
				if neighbour != pData.sender:
					LSPDUpkt = pkt_LSPDU(router_id, pData.router_id, pData.link_id, pData.cost, topology.findLink(router_id, neighbour))
					routerSocket.sendto(LSPDUpkt.toByteArray(), (nse_host, nse_port))
					log.info(LSPDUpkt.log("send", router_id))

			dijkstraCompute()
			log.info(infoBase.printInfoBase())
		else:
			continue




