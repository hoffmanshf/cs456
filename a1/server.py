#!/usr/bin/env python

#CS456 Assignment #1 - Server
#Justin Franchetto
#20375706

#Parameters: None
#Purpose: After client initiation, negotiate a transmission port <r_socket> via TCP.
#	  Wait for a message transmission via UDP on <r_socket>.
#	  Once received, reverse the message and send it back to the client. 
#	  The server will shutdown after a specified <runtime>

from socket import *
import sys, string, random, signal
runtime = 120				#Server runtime before shutting down

#findAvailableSocket(sockType):
#Returns a socket on the first random port available (> 1024)  
def findAvailableSocket(sockType):
	testSocket = socket(AF_INET, sockType)
	testSocket.bind(('', 0))		#Choose a free port
	return testSocket			#Return the socket

#tcpNegotiation():
#Waits for an initiation from the client on <n_socket> via the sending of a predefined request code, <42>.
#Once initialized, a socket is chosen at random for the transaction to be completed. This socket is sent back to the client. 
#Returns: r_socket
def tcpInitiation(n_socket):
	n_socket.listen(1)
	waiting = 1
	while waiting:
		connectionSocket, addr = n_socket.accept()
		initiate = connectionSocket.recv(1024)
        	if int(initiate) == 42:				#Validate request code
			r_socket = findAvailableSocket(SOCK_DGRAM)
			connectionSocket.send(str(r_socket.getsockname()[1]))
			waiting = 0
		else:
			print "Incorrect request code"
	
		connectionSocket.close()

	return r_socket

#udpTransaction(r_socket):
#Listens on <r_socket> for a message transmission from the client. 
#Once received, the message is reversed and send back to the client.
def udpTransaction(r_socket):
     	message, clientAddress = r_socket.recvfrom(2048)
	reversedMessage = message[::-1]
	r_socket.sendto(reversedMessage, clientAddress)
        r_socket.close()

#Shutdown(sigId, frameID):
#Shuts the server down when a signal is triggers. The parameters are not used.
def shutdown(sigID, frameID):
	print "Server will now shutdown..."
	quit()
	
#Main
def main():
	signal.signal(signal.SIGALRM, shutdown)				#Set the signal for shutdown
	signal.alarm(runtime) 
	print "The server will run for " + str(runtime) + " seconds before shutting down"

	n_socket = findAvailableSocket(SOCK_STREAM)
	print "Negotiation port: " + str(n_socket.getsockname()[1])	#Print the negotiation port for the client to use
	
	while True:	
		r_socket = tcpInitiation(n_socket) 			#Wait for initiation
		udpTransaction(r_socket)				#Complete transaction
main()
