# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 13:07
@summary:
@author: Martin Predki
'''

from twisted.protocols.basic import LineReceiver

class TcpProtocol(LineReceiver):
    '''
    @summary: Class for TcpProtocols. A TcpProtocol handles all incoming and outgoing messages
    for the corresponding client. It also gives informations on the connection state.
    '''

    def __init__(self, client):
        '''
        @summary: Creates a new Protocol instance. This function is called by the TcpClientFactory when
        a new network connection is established.
        @param client: A reference to the assigned client.
        @result:
        '''
        self.client = client
        self.client.assignTcpProtocol(self)
        self.address = None

    def connectionMade(self):
        '''
        @summary: This function is called when a network connection is established.
        @result:
        '''
        self.address = self.transport.getPeer()
        self.client.connectionEstablished()

    def connectionLost(self, reason):
        '''
        @summary: This function is called when the connection is lost.
        @param reason:
        @result:
        '''
        self.client.connectionLost(reason)

    def lineReceived(self, line):
        '''
        @summary: This function is called when a line (a line ends with \r\n) is received
        @param line: The received line
        @result:
        '''
        self.client.lineReceived(line)

    def rawDataReceived(self, data):
        '''
        @summary: This function is called when raw data is received (the protocol is set to raw mode)
        @param data: the received data.
        @result:
        '''
        self.client.rawDataReceived(data)

    def sendMessage(self, message):
        '''
        @summary: Sends a message over this connection.
        @param message: The message to send
        @result:
        '''
        self.sendLine(message)

    def sendBytes(self, bytes):
        '''
        @summary: Sends plain bytes over this connection.
        @param bytes: Bytes to send
        @result:
        '''
        self.transport.write(bytes)
