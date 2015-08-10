import struct

NBR_ROUTER = 5

class pkt_HELLO:
	def __init__(self, router_id, link_id):
		self.router_id = router_id
		self.link_id = link_id

	def dataToBytes(self):
		return struct.pack("<II", self.router_id, self.link_id)

	def bytesToData(self, bytes):
		d = struct.unpack("<II", bytes)
		return pkt_HELLO(d[0], d[1])

class pkt_LSPDU:
	def __init__(self, sender, router_id, link_id, cost, via):
		self.sender = sender
		self.router_id = router_id
		self.link_id = link_id
		self.cost = cost
		self.via = via

	def dataToBytes(self):
		return struct.pack("<IIIII", self.sender, self.router_id, self.link_id, self.cost, self.via)

	def bytesToData(self, bytes):
		d = struct.unpack("<IIIII", bytes);
		return pkt_LSPDU(d[0], d[1], d[2], d[3], d[4])

class pkt_INIT:
	def __init__(self, router_id):
		self.router_id = router_id

	def dataToBytes(self):
		return struct.pack("<I", self.router_id);

	def bytesToData(self, bytes):
		d = struct.unpack("<I", bytes);
		self.router_id = d[0]
		return self

class link_cost:
	def __init__(self, link, cost):
		self.link = link
		self.cost = cost

	def dataToBytes(self):
		return struct.pack("<II", self.link, self.cost);

class circuit_DB:
	def __init__(self, nbr_link, linkcost):
		self.nbr_link = nbr_link
		self.linkcost = linkcost

	def dataToBytes(self):
		b = struct.pack("<I", self.nbr_link)
		for lc in self.linkcost:
			b += lc.dataToBytes()
		return b

	def bytesToData(self, bytes):
		self.nbr_link = struct.unpack_from("<I", bytes, 0)[0]
		self.linkcost = []
		for i in range(self.nbr_link):
			d = struct.unpack_from("<II", bytes, i*8 + 4)
			self.linkcost.append(link_cost(d[0], d[1]))
		return self

def bytesToData(bytes):
	l = len(bytes)
	if (l == 8): #hello
		return ("hello", pkt_HELLO.bytesToData(pkt_HELLO(0, 0), bytes))
	elif(l == 20): #lspdu
		return ("lspdu", pkt_LSPDU.bytesToData(pkt_LSPDU(0, 0, 0, 0, 0), bytes))
	elif(l == 4): #init
		return ("init", pkt_INIT.bytesToData(pkt_INIT(0), bytes))
	else: #circuit db
		return ("circuitdb", circuit_DB.bytesToData(circuit_DB(0, []), bytes))
