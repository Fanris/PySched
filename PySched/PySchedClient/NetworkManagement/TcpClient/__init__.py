# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 12:37
@summary: Main class for the TCP Client
@author: Martin Predki
'''


from TcpClientFactory  import TcpClientFactory

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint

import logging

class TcpClient(object):
    '''
    @summary: Main class for the TcpServer.
    '''

    def __init__(self, host, port, networkManager):
        '''
        @summary: Constructor
        @param port: The port on which the TCP server should listen.
        @param networkManager: A reference to the networkManager
        @result:
        '''
        self.logger = logging.getLogger("PySchedClient")
        self.host = host
        self.port = port
        self.server = None
        self.networkManager = networkManager

        self.clientFactory = TcpClientFactory(self)

    def startClient(self):
        '''
        @summary: Starts the TCP server.
        @result:
        '''
        endPoint = TCP4ClientEndpoint(reactor, self.host, self.port)
        endPoint.connect(self.clientFactory)

    def connectionMade(self, client):
        '''
        @summary: Is called when the tcp connections is established.
        @result:
        '''
        self.server = client
        self.networkManager.connectionMade()

    def connectionLost(self, reason):
        '''
        @summary: Is called when the connection to the server is lost.
        @result:
        '''
        self.networkManager.connectionLost(reason)
        self.server = None

    def commandReceived(self, client, command):
        '''
        @summary: Checks if the received command is used for the networkManager or
        pass it to the messageReceiver
        @param client: the origin of the command
        @param command: the command
        @result:
        '''
        self.networkManager.commandReceived(client, command)

    def sendHeartBeat(self):
        '''
        @summary: Sends a heartbeat to the server
        @result: 
        '''
        if self.server:
            self.server.sendHeartBeat()

    def heartBeatResponse(self):
        '''
        @summary: Reacts to the heartBeatResponse
        @result: 
        '''
        self.networkManager.heartBeatResponse()

    def sendMessage(self, message):
        '''
        @summary: Sends a message to a client.
        @param message: the message to send.
        @result:
        '''
        if self.server:
            self.server.sendMessage(message)

    def sendFile(self, pathToFile, md5):
        '''
        @summary: Sends a file to a client.
        @param clientId: the global id or name of the client.
        @param file: the file to send.
        @result:
        '''
        if self.server:
            self.server.sendFile(pathToFile, md5)
            return True

    def receivingFile(self):
        '''
        @summary: is called when a file is about to be received.
        @param pathToFile: path where the file should be stored
        @param md5: md5 hashsum of the file
        @result:
        '''
        self.networkManager.receivingFile()

    def fileTransferCompleted(self, client, pathToFile, md5):
        '''
        @summary: Is called when a file was completely received.
        @param pathToFile: path where the file was stored
        @param md5: md5 hashsum of the original file
        @result:
        '''
        self.logger.debug("File transfer completed. Checking MD5...")
        self.networkManager.fileReceived(client.id, pathToFile, md5)
