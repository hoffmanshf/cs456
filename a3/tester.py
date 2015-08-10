import socket
import packets
from sys import argv
from time import sleep

graph = {}
graph[1] = [[1, 2], 1]
graph[2] = [[2, 3], 2]
graph[3] = [[3, 4], 3]
graph[4] = [[4, 5], 4]
graph[5] = [[5, 1], 5]
graph[6] = [[2, 5], 6]
graph[7] = [[5, 3], 7]

clients = {}
sendDB = True;

def recvInit(init, client):
	global clients
	clients[init.router_id] = client
	print "Recv client init R" + str(init.router_id)

def sendCircuitDB(router, client):
	links = []
	for key, pair in graph.iteritems():
		if (router in pair[0]):
			links.append(packets.link_cost(key, pair[1]))
	send = packets.circuit_DB(len(links), links)
	bytes = send.dataToBytes()
	udpSock.sendto(bytes, client)
	print "Sending DB for R" + str(router)

def forwardHello(hello):
	sendto = 0;
	if (graph[hello.link_id][0][0] == hello.router_id):
		sendto = graph[hello.link_id][0][1]
	elif (graph[hello.link_id][0][1] == hello.router_id):
		sendto = graph[hello.link_id][0][0]
	else:
		raise Exception("node sent hello over link it does not have!")
	bytes = hello.dataToBytes()
	udpSock.sendto(bytes, clients[sendto])
	print "R" + str(hello.router_id) + " sent hello to R" + str(sendto)

def forwardLSPDU(lspdu):
	sendto = 0;
	if (graph[lspdu.via][0][0] == lspdu.sender):
		sendto = graph[lspdu.via][0][1]
	elif (graph[lspdu.via][0][1] == lspdu.sender):
		sendto = graph[lspdu.via][0][0]
	else:
		st = str(lspdu.sender) + str(lspdu.via) + " to " + str(sendto)
		print st
		raise Exception("node sent LSPDU over link it does not have!" )

	bytes = lspdu.dataToBytes()
	udpSock.sendto(bytes, clients[sendto])
	print "R" + str(lspdu.sender) + "send lspdu to R" + str(sendto)
	print "##########R" + str(lspdu.router_id) + " has  " + str(lspdu.link_id)

host = argv[1]
port = int(argv[2])

udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.bind(("", port))

while True:
	data, client = udpSock.recvfrom(4096)
	recv = packets.bytesToData(data)

	if (recv[0] == 'init'):
		recvInit(recv[1], client)
	elif (recv[0] == 'hello'):
		forwardHello(recv[1])
	elif (recv[0] == 'lspdu'):
		forwardLSPDU(recv[1])
	else:
		raise Exception("Emulator received packets it does not recognize!")
	
	if (sendDB and len(clients) == 5):
		for router, client in clients.iteritems():		
			sendCircuitDB(router, client)
		sendDB = False
	elif(sendDB):
		print "Length of clients " + str(len(clients))
