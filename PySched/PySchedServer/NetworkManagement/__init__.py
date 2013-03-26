# -*- coding: utf-8 -*-
'''
Created on 2013-01-11 13:21
@summary:
@author: Martin Predki
'''
from PySched.Common.IO import FileUtils

from PySched.Common.Interfaces.Network.NetworkInterface import NetworkInterface
from PySched.Common.IO.FileUtils import getFileMD5Hashsum, deleteFile

from UdpServer import UdpServer
from TcpServer import TcpServer

import os
import logging


class NetworkManager(NetworkInterface):
    '''
    @summary: A NetworkManager.
    '''

    def __init__(self, workingDir, messageReceiver):
        '''
        @summary: Initializes this NetworkManager.
        @param messageReceiver: A MessageReceiver. See Common.Interfaces.Network.MessageReceiverInterface
        @result:
        '''        
        self.logger = logging.getLogger("PySchedServer")
        self.workingDir = os.path.join(workingDir, "network")
        FileUtils.createDirectory(self.workingDir)

        self.messageReceiver = messageReceiver
        self.tcpServer = None
        self.udpServer = None

        self.udpPort = 50000
        self.tcpPort = 49999
        self.udpMultigroup = "228.0.0.5"

    def startService(self):
        '''
        @summary: Starts the Network services
        @result:
        '''
        self.logger.info("Starting udp server...")
        self.udpServer = UdpServer(self.udpPort, self.udpMultigroup)
        self.udpServer.startServer()

        self.logger.info("Starting tcp server...")
        self.tcpServer = TcpServer(self.tcpPort, self)
        self.tcpServer.startServer()

    def stopService(self):
        self.logger.info("Shutting down udp server...")
        self.udpServer.stopServer()

        self.logger.info("Shutting down tcp server...")
        self.tcpServer.stopServer()


    def connectionMade(self, networkId):
        self.messageReceiver.connectionMade(networkId)

    def connectionLost(self, networkId):
        self.messageReceiver.connectionLost(networkId)


    def commandReceived(self, client, command):
        '''
        @summary: passes a received command to the messageReceiver
        @param client: the origin of the command
        @param command: the command
        @result:
        '''
        self.messageReceiver.messageReceived(client.id, command)

    def sendMessage(self, receiver, message):
        '''
        @summary: Sends a Message
        @param receiver: the receiver of the message
        @param message: the message
        @result:
        '''
        self.logger.debug("Sending message to {}: {}".format(receiver, message))
        self.tcpServer.sendMessage(receiver, message)

    def sendFile(self, receiver, pathToFile):
        '''
        @summary: Sends a File
        @param receiver: the receiver of the file
        @param pathToFile: the path to the file
        @result:
        '''
        md5 = getFileMD5Hashsum(pathToFile)
        return self.tcpServer.sendFile(receiver, pathToFile, md5)

    def fileReceived(self, networkId, pathToFile, md5):
        self.messageReceiver.fileTransferCompleted(networkId, pathToFile)
        deleteFile(pathToFile)
