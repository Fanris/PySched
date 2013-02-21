# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 13:37
@summary:
@author: Martin Predki
'''

from twisted.internet.protocol import DatagramProtocol

class UdpProtocol(DatagramProtocol):
    '''
    @summary: The Protocol class handles all incoming and outgoing communication
    with the udp server.
    '''

    def __init__(self, udpServer):
        '''
        @summary: Constructor for the UDP Protocol.
        @param udpServer: A reference to the UdpServer
        '''
        self.udpServer = udpServer
        self.id = "UDP"

    def sendBroadcast(self, message):
        '''
        @summary: Broadcasts the given message to the Multicast Group
        @param message: The message to send
        '''
        self.transport.write(message, (self.udpServer.multicastGroup, self.udpServer.port))


    def datagramReceived(self, data, (host, port)):
        '''
        @summary: This function is called when a datagram is received.
        @param data: the received data
        @param (host, port): A tupel containing the address of the sender
        @result:
        '''
        self.udpServer.messageReceived(data, host)

    def startProtocol(self):
        '''
        @summary: Called after protocol has started listening.
        '''
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(1)

        # Join a specific multicast group:
        self.transport.joinGroup(self.udpServer.multicastGroup)

        # Create LoopingCall to Broadcast "Server available" every 30 sec
        self.udpServer.sendServerAvailableBroadcast()
