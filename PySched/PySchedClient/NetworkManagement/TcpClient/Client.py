# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 13:25
@summary:
@author: Martin Predki
'''

from PySched.Common.IO.FileUtils import readBytesFromFile

import json
import os
import logging
import base64

class Client(object):
    '''
    @summary: This class represents a network client. This could be either a workstation
    or a user.
    '''
    __id = 0

    def __init__(self, tcpClient):
        '''
        @summary: Initializes a client object.
        @param tcpProtocol: A reference to the corresponding TcpProtocol
        @param commandParser: A reference to the command parser
        @result:
        '''
        self.id = Client.__id
        Client.__id += 1

        self.tcpProtocol = None
        self.tcpClient = tcpClient

        # attributes for file transfer:
        self.currentFilePath = None
        self.currentFile = None
        self.currentMD5 = None

        self.logger = logging.getLogger("PySchedClient")

    def assignTcpProtocol(self, tcpProtocol):
        '''
        @summary: Assigns the given TcpProtocol to this client.
        @param tcpProtocol: The TcpProtocol
        @result:
        '''
        self.tcpProtocol = tcpProtocol;

    def connectionEstablished(self):
        '''
        @summary: Is called by the protocol, when the tcp connection is established.
        @result:
        '''
        self.tcpClient.connectionMade(self)


    def connectionLost(self, reason):
        '''
        @summary: Is called when the network connection is lost
        @param reason: Reason for the connection lost
        @result:
        '''
        self.tcpClient.connectionLost(reason)

    def lineReceived(self, line):
        '''
        @summary: Is called when a line is received.
        @param line: The received line
        @result:
        '''
        cmd = json.loads(line, encoding="ISO-8859-1")
        networkCommand = cmd.get("nCommand", "")

        if networkCommand == "heartBeatResponse":            
            self.tcpClient.heartBeatResponse()
            return            

        self.tcpClient.commandReceived(self, line)

    def sendHeartBeat(self):
        '''
        @summary: Sends a heartbeat to the server.
        @result: 
        '''
        cmd = json.dumps({"nCommand": "heartbeat"})
        self.sendMessage(cmd)

    def sendMessage(self, message):
        '''
        @summary: Sends a message to the client.
        @param message: The message to send
        @result:
        '''
        self.tcpProtocol.sendMessage(message)
