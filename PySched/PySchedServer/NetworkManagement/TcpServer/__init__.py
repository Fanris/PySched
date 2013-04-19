# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 12:37
@summary: Main class for the TCP Server
@author: Martin Predki
'''

from TcpClientFactory  import TcpClientFactory

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import logging

class TcpServer(object):
    '''
    @summary: Main class for the TcpServer.
    '''

    def __init__(self, port, networkManager):
        '''
        @summary:           Constructor
        @param port:        The port on which the TCP server should listen.
        @param pySchedServer: A reference to the PySchedServer
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
        self.port = port
        self.networkManager = networkManager
        self.clientFactory = TcpClientFactory(self)
        self.clients = []

    def startServer(self):
        '''
        @summary:           Starts the TCP server.
        @result:
        '''
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(self.clientFactory)

        self.logger.info("TCP Server started on port {}.".format(self.port))

    def stopServer(self):
        pass

    def connectionMade(self, client):
        '''
        @summary:           Is called when a new connection is established
        @param client:      the new client
        @result:
        '''
        self.clients.append(client)
        self.networkManager.connectionMade(client.id)

    def connectionLost(self, client):
        '''
        @summary:           Is called when a connection is lost.
        @param client:      the client which lost the connection
        @result:
        '''
        self.clients.remove(client)
        self.networkManager.connectionLost(client.id)


    def commandReceived(self, client, command):
        '''
        @summary:           Checks if the received command is used for the 
                            networkManager or pass it to the messageReceiver
        @param client:      the origin of the command
        @param command:     the command
        @result:
        '''
        self.networkManager.commandReceived(client, command)

    def getClients(self):
        '''
        @summary:           Returns a dictionary with all currently connected 
                            clients
        @result:            A dictionary containing all client with their id as key
        '''
        return self.clients

    def getClient(self, identifier):
        '''
        @summary:           Returns the client with the specified id.
        @param identifier:  The id or name of the client.
        @result:            a Client object
        '''
        for client in self.clients:
            if client.id == identifier:
                return client


    def sendMessage(self, identifier, message):
        '''
        @summary:           Sends a message to a client.
        @param identifier:  the global id or name of the client.
        @param message:     the message to send.
        @result:
        '''
        client = self.getClient(identifier)

        if client:
            client.sendMessage(message)
            return True


    def sendFile(self, identifier, pathToFile, md5):
        '''
        @summary:           Sends a file to a client.
        @param identifier:  the global id or name of the client.
        @param file:        the file to send.
        @result:
        '''
        client = self.getClient(identifier)
        if client:
            return client.sendFile(pathToFile, md5)            

    def fileTransferCompleted(self, client, pathToFile, md5):
        '''
        @summary:           Is called when a file was completely received.
        @param pathToFile:  path where the file was stored
        @param md5:         md5 hashsum of the original file
        @result:
        '''
        self.logger.debug("File transfer completed. Checking MD5...")
        self.networkManager.fileReceived(client.id, pathToFile, md5)
