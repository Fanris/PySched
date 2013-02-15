# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 12:51
@summary:
@author: Martin Predki
'''

from twisted.internet.protocol import ClientFactory

from Client import Client
from TcpProtocol import TcpProtocol

class TcpClientFactory(ClientFactory):
    '''
    @summary: Class to create Client objects and TCP-protocols. It also holds a list
    of all currently connected clients.
    '''

    def __init__(self, tcpClient):
        '''
        @summary: Initializes the class.
        @param commandParser: A reference to the command parser.
        @result:
        '''
        self.server = None
        self.tcpClient = tcpClient

        self.nextTmpFileId = 0

    def buildProtocol(self, addr):
        '''
        @summary: Creates an instance of the TcpProtocol class.
        @result:
        '''
        client = Client(self.tcpClient)
        tcpProtocol = TcpProtocol(client)
        return tcpProtocol
