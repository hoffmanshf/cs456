#!/usr/bin/env python

#CS456 Assignment #1 - Client
#Justin Franchetto
#20375706

#Parameters: <server_address> <n_port> <msg>
#Purpose: Initiate a TCP connection with the <server_address> at the <n_port> by sending an integer over the socket
#	  Using the port sent back by the server <r_port>, send back the <msg> over a UDP socket
#   	  Receive the reversed message from the server and print it out

from socket import *
import sys, string

#tcpInitiation(server_address, n_port):
#Initiates a transaction with the <server_address> via TCP at <n_port> by sending the predefined request code <42>. 
#The server sends back the port needed for the transaction.
#Returns: r_port
def tcpInitiation(server_address, n_port):
	try:
		TCPSocket = socket(AF_INET, SOCK_STREAM)
		TCPSocket.connect((server_address, n_port))
	except error, e:
		print "Negotiation port unavailable: please ensure the server is running"
		quit()

	TCPSocket.send("42")			
	r_port = int(TCPSocket.recv(1024))
	TCPSocket.close()
	return r_port

#udpTransaction(sever_address, n_port):
#Completes a transaction with the <server_address> via UDP at <r_port> by sending the string, <msg>. The server will reverse the string and send back the result.
#Returns: ReversedString
def udpTransaction(server_address, r_port, msg):
	UDPSocket = socket(AF_INET, SOCK_DGRAM)
	UDPSocket.sendto(msg, (server_address, r_port))
	reversedMessage, serverAddress = UDPSocket.recvfrom(2048)
	UDPSocket.close()
	return reversedMessage

#Main
def main():
	if len(sys.argv) == 4:							#Argument validation
		server_address = sys.argv[1]
		n_port = int(sys.argv[2])
		msg = sys.argv[3]

		r_port = tcpInitiation(server_address, n_port)			#Initiate the TCP connection with the server, receive the r_port
		reversedMessage = udpTransaction(server_address, r_port, msg)	#Complete the transaction using UDP, receive the reversed message
		print reversedMessage
	else:
		print "Error: incorrect parameters. <server_address> <n_port> and <msg> are required"
		quit()

main()
