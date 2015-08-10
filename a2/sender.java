//CS456 - Assignment #2 - Sender
//Justin Franchetto
//20375706

//Purpose: The Sender is to read contents from the specified file,
//separate the content into packets and send to the receiver via the emulator,
//using the specified port. The sender will send packets according to the
//Go-Back-N protocol, until all packets, including the EOT packet
// have been ACKed by the receiver.

//Parameters:
//<host address of the network emulator>,
//<UDP port number used by the emulator to receive data from the sender>,
//<UDP port number used by the sender to receive ACKs from the emulator>,
//<name of the file to be transferred>

import java.io.*;
import java.net.*;
import java.io.FileInputStream;
import java.io.PrintWriter;

class Sender {
    
    static final int packetDataSize = packet.maxDataLength;
    static final int windowSize = 10;
    static final int timeoutLength = 500;
    static final int seqMod = packet.SeqNumModulo;
    
    //receiveACKs(int senderRecvPort, PrintWriter ackWriter):
    //Receive ACKs from the receiver, return the seqnum of received ACK
    //Write the sequence numbers received to the given writer.
    static int receiveACKs(int senderRecvPort, PrintWriter ackWriter) throws Exception
    {
        //Receiving socket setup
        byte[] receiveData = new byte[512];
        DatagramSocket ackSocket = new DatagramSocket(senderRecvPort);
        ackSocket.setSoTimeout(timeoutLength);
        DatagramPacket ackPacket = new DatagramPacket(receiveData, receiveData.length);
        
        //Receive packet
        try{
            ackSocket.receive(ackPacket);
        }
        catch(SocketTimeoutException e){
            ackSocket.close();
            return -1;
        }
        finally{
            ackSocket.close();
        }
        
        //Extract packet, get the sequence number and log it
        packet recvPacket = packet.parseUDPdata(receiveData);
        int seqRecv = recvPacket.getSeqNum();
        ackWriter.println(seqRecv);
        return seqRecv;
    }
    
    //sendPackets(packet packets[], int initialPacket, String hostAddress, int destPort,
    //int sendNum, PrintWriter seqWriter):
    //Send <sendNum> packets in packets[] array starting at <initialPacket> to the <destPort> on <hostAddress>.
    //Log the sequence number of packets sent in the <seqWriter>
    //Return the number of packets actually sent
    static int sendPackets(packet packets[], int initialPacket, String hostAddress, int destPort, int sendNum, PrintWriter seqWriter) throws Exception
    {
        DatagramSocket clientSocket = new DatagramSocket();
        InetAddress IPAddress = InetAddress.getByName(hostAddress);
        
        int sent = 0;
        for (int i=initialPacket;(i<packets.length && i<initialPacket+sendNum); i++){
            //Construct a Datagram out of the data in our packet and send it
            byte[] sendData = packets[i].getUDPdata();
            DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, IPAddress, destPort);
            clientSocket.send(sendPacket);
            sent++;
            seqWriter.println(packets[i].getSeqNum());	//Log the sequence number of packet sent
        }
        return sent;
    }
    
    //getPackets(byte content[]):
    //Accept a byte array and return an array of packets to be sent
    static packet[] getPackets(byte content[]) throws Exception
    {
        //Calculate number of packets that need to be created
        int numPackets = (int)Math.ceil((double)content.length/(double)packetDataSize);
        packet packets[] = new packet[numPackets];
        
        //Construct the array of packets
        for(int i=0, j=0; i<numPackets; i++, j+=packetDataSize){
            byte data[] = new byte[Math.min(packetDataSize, content.length-j)];	//Either a full packet, or the last packet
            System.arraycopy(content, j, data, 0, Math.min(packetDataSize, content.length-j));
            packets[i] = packet.createPacket(i%seqMod, new String(data));
        }
        return packets;
    }
    
    //getContent(String fileName):
    //Read the contents of the file, <fileName> and return a byte array
    //containing those contents.
    static byte[] getContent(String fileName) throws Exception
    {
        byte content[] = null;
        FileInputStream contentStream = null;
        
        try{
            File contentFile = new File(fileName);
            content = new byte[(int)contentFile.length()];
            contentStream = new FileInputStream(contentFile);
            contentStream.read(content);
        }
        catch(FileNotFoundException e){
            System.out.println("File not found:\n" + e);
        }
        finally{
            if(contentStream != null){
                contentStream.close();
            }
        }
        return content;
    }
    
    public static void main(String args[]) throws Exception
    {
        String emuAddress = null;
        String fileName = null;
        int emuRecvPort = 0;
        int senderRecvPort = 0;
        PrintWriter seqWriter = new PrintWriter("seqnum.log", "UTF-8");
        PrintWriter ackWriter = new PrintWriter("ack.log", "UTF-8");
        
        if (args.length != 4){
            System.out.println("Invalid parameters");
            System.exit(1);
        }
        else{
            emuAddress = args[0];
            emuRecvPort = Integer.parseInt(args[1]);
            senderRecvPort = Integer.parseInt(args[2]);
            fileName = args[3];
        }
        
        //Read the contents of the file into a byte array and process into an array of packets.
        byte content[] = getContent(fileName);
        packet packets[] = getPackets(content);
        
        //Send data to the receiver, via the network emulator
        //We will continue to send until all packets have been ACKed
        int packetsACKed = 0;
        int packetsOut = 0;
        int initialPacket = -1;
        
        while(packetsACKed < packets.length){
            int packetsSent = 0;
            int firstSent = initialPacket+1+packetsOut;	//We start sending packets at the next not in flight packet
            
            //Send packets
            if(firstSent < packets.length){
                packetsSent = sendPackets(packets, firstSent, emuAddress, emuRecvPort, (windowSize-packetsOut), seqWriter);
            }
            packetsOut = packetsOut + packetsSent;
            
            int ACKed = 0;
            do{
                ACKed = 0;
                //Check for ACKs
                int recvACK = receiveACKs(senderRecvPort, ackWriter);
                if(recvACK == -1){			//Timeout: reset number of sent packets and loop again
                    packetsOut = 0;
                }else{
                    //Count packets received sicne last ACK
                    while(((seqMod+initialPacket+ACKed) % seqMod) != recvACK) ACKed++;
                    if(ACKed <= windowSize){
                        initialPacket = initialPacket + ACKed;		//Adjust the starting packet for next send
                        packetsOut = packetsOut - ACKed;		//Adjust the amount of packets outstanding
                        packetsACKed = packetsACKed + ACKed;		//Update total ACKed packets
                    }
                }
            } while(ACKed > windowSize);
        }
        
        //All packets have been ACKed -> Send an EOT packet to the receiver
        packet eotPackets[] = new packet[1];
        eotPackets[0] = packet.createEOT((packets.length)%seqMod);
        sendPackets(eotPackets, 0, emuAddress, emuRecvPort, 1, seqWriter);
        
        //Close after all ACKs have been received
        while(true){
            int recvACK = receiveACKs(senderRecvPort, ackWriter);
            if(recvACK == eotPackets[0].getSeqNum()){
                seqWriter.close();
                ackWriter.close();
                return;
            }
        }
        
    }
}
