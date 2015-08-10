#!/usr/bin/python

#CS456 Assignment #3 - packetOps
#Justin Franchetto
#20375706

#Provides packet structures and operations for creating, reading,
#logging and packing into byte arrays

import struct

def NBR_ROUTER():
	return 5

#Analyzes a unknown byte array to determine the type of packet, 
#Creates a packet of appropriate type and returns it
def getPacket(bytes, db = False):
	length = len(bytes)
	
	if db:
		nbr_link = struct.unpack_from("<I", bytes, 0)[0]
		linkcost = list()		
		for x in range(nbr_link):
			data = struct.unpack_from("<II", bytes, (x*8) +4)
			linkcost.append(link_cost(data[0], data[1]))		
		return ("CIRCUIT_DB", circuit_DB(nbr_link, linkcost))
	
	if length == 8:			#pkt_INIT
		data = struct.unpack("<II", bytes)
		return ("HELLO", pkt_HELLO(data[0], data[1]))
	elif length == 20:		#pkt_LSPDU
		data = struct.unpack("<IIIII", bytes)
		return ("LSPDU", pkt_LSPDU(data[0], data[1], data[2], data[3], data[4]))
	elif length == 4:		#pkt_INIT
		data = struct.unpack("<I", bytes)
		return ("INIT", pkt_INIT(data[0]))
	else:
		print "No buen"

################
#Packet Definitions

#Hello Packet
class pkt_HELLO:
	def __init__(self, router_id, link_id):
		self.router_id = router_id
		self.link_id = link_id

	def toByteArray(self):
		return struct.pack("<II", self.router_id, self.link_id)

	def log(self, op, router):
		if op == "send":
			return "R" + str(router) + " sends a HELLO: router_id " + str(self.router_id) + ", link_id " + str(self.link_id)
		else: 
			return "R" + str(router) + " receives a HELLO: router_id " + str(self.router_id) + ", link_id " + str(self.link_id)

#LSPDU Packet
class pkt_LSPDU:
	def __init__(self, sender, router_id, link_id, cost, via):
		self.sender = sender	
		self.router_id = router_id
		self.link_id = link_id
		self.cost = cost
		self.via = via

	def toByteArray(self):
		return struct.pack("<IIIII", self.sender, self.router_id, self.link_id, self.cost, self.via)

	def log(self, op, router):
		if op == "send":
			return "R" + str(router) + " sends an LSPDU: sender " + str(self.sender) + ", router_id " + str(self.router_id) + ", link_id " + str(self.link_id) + ", cost " + str(self.cost) + ", via " + str(self.via)
		else: 
			return "R" + str(router) + " receives an LSPDU: sender " + str(self.sender) + ", router_id " + str(self.router_id) + ", link_id " + str(self.link_id) + ", cost " + str(self.cost) + ", via " + str(self.via)

#INIT Packet
class pkt_INIT:
	def __init__(self, router_id):
		self.router_id = router_id

	def toByteArray(self):
		return struct.pack("<I", self.router_id)

	def log(self, op, router):
		if op == "send":
			return "R" + str(router) + " sends an INIT: router_id " + str(self.router_id) 
		else: 
			return "R" + str(router) + " receives an INIT: router_id " + str(self.router_id)

#Link Cost Pair
class link_cost:
	def __init__(self, link, cost):
		self.link = link
		self.cost = cost

	def toByteArray(self):
		return struct.pack("<II", self.link, self.cost)

#Circuit DB Packet
class circuit_DB:
	def __init__(self, nbr_link, linkcost):
		self.nbr_link = nbr_link
		self.linkcost = linkcost

	def toByteArray(self):
		by = struct.pack("<I", self.nbr_link)
		for link in self.linkcost:
			by = by + link.toByteArray()
		return by

	def log(self, op, router):
		if op == "send":
			logStr = "R" + str(router) + " sends a CIRCUIT_DB: nbr_link " + str(self.nbr_link) + " with links: \n" 
			for entry in self.linkcost:
				logStr = logStr + "\t link " + str(entry.link) + ", cost " + str(entry.cost) + "\n"
			return logStr
		else: 
			logStr = "R" + str(router) + " receives a CIRCUIT_DB: nbr_link " + str(self.nbr_link) + " with links: \n" 
			for entry in self.linkcost:
				logStr = logStr + "\t link " + str(entry.link) + ", cost " + str(entry.cost) + "\n"
			return logStr

