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

    def __init__(self, udpClient):
        '''
        @summary: Constructor for the UDP Protocol.
        @param udpServer: A reference to the UdpServer
        '''
        self.udpClient = udpClient
        self.id = "UDP"

    def sendBroadcast(self, message):
        '''
        @summary: Broadcasts the given message to the Multicast Group
        @param message: The message to send
        '''
        self.transport.write(message, (self.udpClient.multicastGroup, self.udpClient.port))

    def datagramReceived(self, data, (host, port)):
        '''
        @summary: Is called if an udp datagram is received.
        @param data: the received data.
        @param : host and port of the sender
        @result:
        '''
        self.udpClient.messageReceived(data, host)

    def startProtocol(self):
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(1)

        # Join a specific multicast group:
        self.transport.joinGroup(self.udpClient.multicastGroup)
        self.udpClient.sendPing()
