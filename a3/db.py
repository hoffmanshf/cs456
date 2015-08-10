#!/usr/bin/python

#CS456 Assignment #3 - Databases
#Justin Franchetto
#20375706
#Provides the database structures, and functions for:
#Creating, updating, searching and logging those structures

import copy

#RIB: Router information base
#Holds the path with minimal cost to each destination router
class RIB:
	def __init__(self, router_id, size):
		self.id = router_id
		self.table = dict()
		for x in range(1, size+1):
			if x == router_id:
				self.table[x] = ("Local", 0)
			else:
				self.table[x] = ("inf", float("inf")) 

	def addDest(self, dest, path, cost):
		if not(dest in self.table):
			self.table[dest] = (path, cost)
		elif dest in self.table:
			if cost < self.table[dest][1]:
				self.table[dest] = (path, cost)
	
	def printInfoBase(self):
		outString = '\n' + "#RIB:" + '\n'
		for router, entry in self.table.iteritems():
			outString = outString + "R" + str(self.id) + " -> " + "R" + str(router) 
			if(str(entry[0]) == "Local") or (str(entry[0]) == "inf"):
				outString = outString + " -> " + str(entry[0]) + "," + str(entry[1]) + "\n"
			else:
				outString = outString + " -> R" + str(entry[0]) + "," + str(entry[1]) + "\n"
		return outString + "################################" + '\n'

#topEntry: a single entry in the topological database
#Functions for updating a single entry in the DB
class topEntry:
	def __init__(self, nbr, link, cost, dest):
		self.nbr = nbr
		self.lc = [(link, cost, dest)]

	def updateEntry(self, link, cost, dest):			
		change = False
		for i in range(len(self.lc)): 
			if self.lc[i][0] == link and self.lc[i][1] == cost:
				if not(self.lc[i][2] == dest):
					self.lc[i] = (link, cost, dest)
					change = True
					return change
	
		if not((link, cost, dest) in self.lc):
			self.nbr = self.nbr + 1
			self.lc.append((link, cost, dest))
			change = True

		return change

#Topological database:
#Contains the topological information about the routers
#Functions for creating, updating and printing the DB
class topDB:
	def __init__(self, router):
		self.id = router;
		self.link_table = dict()

	def computeDest(self, router, link):
		for node in self.link_table:
			if node != router:
				for pair in self.link_table[node].lc:
					if pair[0] == link:
						return node
		return None

	#Update and existing link
	def updateLink(self, router, link):
		change = False
		cost = None
		for entry in self.link_table[self.id].lc:
			if entry[0] == link: 
				cost = entry[1]
		self.link_table[self.id].updateEntry(link, cost, router)
	
	#Add a new link	
	def addLink(self, router, link, cost):
		change = False
		dest = None
		if not(router in self.link_table):
			dest = self.computeDest(router, link)
			self.link_table[router] = topEntry(1, link, cost, dest)	
			change = True	
		else:	
			dest = self.computeDest(router, link)	
			change = self.link_table[router].updateEntry(link, cost, dest)
		
		if change and not(dest == None):	
			self.link_table[dest].updateEntry(link, cost, router)
		return change

	#Find the link between two routers, if it exists
	def findLink(self, router, neighbour):
		link = None
		for entry in self.link_table[router].lc:
			if entry[2] == neighbour:
				link = entry[0]
		return link

	#Find the cost to get from source to dest router, if possible
	def findCost(self, router, dest):
		cost = float('inf')
		if(router in self.link_table):
			for entry in self.link_table[router].lc:
				if entry[2] == dest:
					cost = entry[1]
			return cost

	#Find a router's neighbours
	def findNeighbours(self, router):
		neighbours = list()
		if(router in self.link_table):
			for entry in self.link_table[router].lc:
				if(entry[2] != None):
					neighbours.append(entry[2])
		return neighbours

	def printTopology(self):		
		outString = '\n' + "#Topology Database:" + '\n'
		for router, entry in self.link_table.iteritems():
			outString = outString + "R" + str(self.id) + " -> " + "R" + str(router) + " nbr link " + str(entry.nbr) + "\n"
			for pair in entry.lc:
				outString = outString + "R" + str(self.id) + " -> " + "R" + str(router) + " link " + str(pair[0]) + " cost " + str(pair[1]) + '\n'
				#" dest " + str(pair[2]) + "\n"
		return outString + "################################" + '\n'
