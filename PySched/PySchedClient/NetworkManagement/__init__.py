# -*- coding: utf-8 -*-
'''
Created on 2013-01-09 15:11
@summary:
@author: Martin Predki
'''

from PySched.Common.Interfaces.Network.NetworkInterface import NetworkInterface
from PySched.Common.IO.FileUtils import getFileMD5Hashsum, deleteFile

from TcpClient import TcpClient
from UdpClient import UdpClient
from SSH import SSHTunnel

import logging

class NetworkManager(NetworkInterface):
    '''
    @summary: A NetworkManager.
    '''

    def __init__(self, workingDir, messageReceiver, pathToRsa):
        '''
        @summary: Initializes this NetworkManager.
        @param messageReceiver: A MessageReceiver.
        See Common.Interfaces.Network.MessageReceiverInterface
        @result:
        '''
        self.logger = logging.getLogger("PySchedClient")
        super(NetworkManager, self).__init__(workingDir, messageReceiver, pathToRsa)

        self.tcpClient = None
        self.udpClient = None
        self.sshTunnel = None

        self.udpPort = 50000
        self.tcpPort = 49999
        self.udpMultigroup = "228.0.0.5"

        self.__retryCounter = 0

    def startService(self):
        '''
        @summary: Starts the Network services
        @result:
        '''
        self.logger.info("Starting udp server...")
        self.udpClient = UdpClient(self.udpPort, self.udpMultigroup, self)
        self.udpClient.startClient()

    def serverFound(self, host):
        '''
        @summary: Is called when a server is found via udp
        @result:
        '''
        self.logger.info("Server found.")
        self.udpClient.stopClient()

        self.sshTunnel = SSHTunnel(host=host, keyFile=self.pathToRsa)

        localPort = self.sshTunnel.buildTunnel()
        if localPort:
            self.connectTcp(localPort)

    def connectTcp(self, localPort):
        '''
        @summary: Connects to an ssh tunnel
        @result:
        '''
        self.logger.info("Building tcp connection to localhost:{}".format(localPort))
        self.tcpClient = TcpClient('localhost', localPort, self)
        self.tcpClient.startClient()

    def connectionMade(self):
        '''
        @summary: Is called when the tcp connection is established.
        @result:
        '''
        self.logger.info("Tcp connection established.")
        self.messageReceiver.connectionBuild(self.tcpClient.server.id)

    def connectionLost(self):
        '''
        @summary: Is called when the tcp connection is lost
        @result:
        '''
        self.logger.info("Tcp connection lost.")
        self.messageReceiver.connectionLost(self.tcpClient.server.id)
        self.tcpClient = None
        self.sshTunnel.closeTunnel()

        self.logger.info("Restarting the udp listener")
        self.startService()

    def commandReceived(self, client, command):
        '''
        @summary: passes a received command to the messageReceiver
        @param client: the origin of the command
        @param command: the command
        @result:
        '''
        self.messageReceiver.messageReceived(client, command)

    def sendMessage(self, receiver, message):
        '''
        @summary: Sends a Message
        @param receiver: the receiver of the message
        @param message: the message
        @result:
        '''
        self.tcpClient.sendMessage(message)

    def sendFile(self, receiver, pathToFile):
        '''
        @summary: Sends a File
        @param receiver: the receiver of the file
        @param pathToFile: the path to the file
        @result:
        '''
        if self.tcpClient:
            md5 = getFileMD5Hashsum(pathToFile)
            return self.tcpClient.sendFile(pathToFile, md5)
        else:
            return False

    def fileReceived(self, networkId, pathToFile, md5):
        self.messageReceiver.fileTransferCompleted(networkId, pathToFile)
        deleteFile(pathToFile)
