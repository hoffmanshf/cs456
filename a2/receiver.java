//CS456 - Assignment #2 - Receiver
//Justin Franchetto
//20375706

//Purpose: The Receiver is to receive packets from the sender
//via the emulator. The receiver will send back ACKs if the packet
//received matches the expected sequence number. Upon receiving the EOT packet,
//send back an EOT and close.

//Parameters:
//<hostname for the network emulator>,
//<UDP port number used by the link emulator to receive ACKs from the receiver>,
//<UDP port number used by the receiver to receive data from the emulator>,
//<name of the file into which the received data is written>

import java.io.*;
import java.net.*;
import java.io.PrintWriter;

class Receiver {
    
    static final int seqMod = packet.SeqNumModulo;
    
    public static void main(String args[]) throws Exception
    {
        String emuAddress = null;
        String fileName = null;
        int emuRecvPort = 0;
        int receiverRecvPort = 0;
        
        if (args.length != 4){
            System.out.println("Invalid parameters");
            System.exit(1);
        }
        else{
            emuAddress = args[0];
            emuRecvPort = Integer.parseInt(args[1]);
            receiverRecvPort = Integer.parseInt(args[2]);
            fileName = args[3];
        }
        
        PrintWriter outputWriter = new PrintWriter(fileName, "UTF-8");
        PrintWriter seqWriter = new PrintWriter("arrival.log", "UTF-8");
        
        DatagramSocket serverSocket = new DatagramSocket(receiverRecvPort);
        DatagramSocket outSocket = new DatagramSocket();
        
        byte[] receiveData = new byte[1024];
        byte[] sendData  = new byte[1024];
        
        int expectedSeq = 0;
        int packetSeq = 0;
        boolean packetZero = false;  //First packet?
        
        while(true)
        {
            //Setup receiving socket and extract the packet
            DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
            serverSocket.receive(receivePacket);
            packet recvPacket = packet.parseUDPdata(receivePacket.getData());
            
            byte recvData[] = recvPacket.getData();
            seqWriter.println(recvPacket.getSeqNum());        //Log the received sequence number
            
            packet ACK = null;
            if(recvPacket.getSeqNum() == expectedSeq){
                packetZero = true;                           //First packet received
                packetSeq = recvPacket.getSeqNum();	     //Correct packet received, ACK it
                expectedSeq = (expectedSeq+1)%seqMod;
                
                if(recvPacket.getType() == 1){               //Write to output, only if this is a data packet and expected
                    outputWriter.print(new String(recvPacket.getData()));
                }
            }else if(!packetZero){
                //The first packet has yet to be received, skip this packet
                continue;
            }
            else {
                packetSeq = (seqMod + (expectedSeq-1))%seqMod;		//Wrong packet received, ACK last ACKed
            }
            
            if (recvPacket.getType() == 2){                //EOT received
                ACK = packet.createEOT(packetSeq);
                Thread.sleep(1000);                        //Sleep here to allow the sender time to be ready for EOT
            }else{
                ACK = packet.createACK(packetSeq);
            }
            
            //Send the prepared packet, either an ACK or an EOT
            InetAddress IPAddress = InetAddress.getByName(emuAddress);
            byte ackData[] = ACK.getUDPdata();
            DatagramPacket sendPacket = new DatagramPacket(ackData, ackData.length, IPAddress, emuRecvPort);
            outSocket.send(sendPacket);
            
            //If an EOT was sent, we close the logs and end the program.
            if(ACK.getType() == 2){
                seqWriter.close();
                outputWriter.close();
                break;
            }
        }
    }
}
