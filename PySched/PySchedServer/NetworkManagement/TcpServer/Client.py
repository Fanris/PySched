# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 13:25
@summary:
@author: Martin Predki
'''


from PySched.Common.IO.FileUtils import readBytesFromFile

import logging
import json
import os
import base64

class Client(object):
    '''
    @summary: This class represents a network client. This could be either a workstation
    or a user.
    '''
    __id = 0

    def __init__(self, tcpServer):
        '''
        @summary: Initializes a client object.
        @param tcpProtocol: A reference to the corresponding TcpProtocol
        @param commandParser: A reference to the command parser
        @result:
        '''
        self.id = Client.__id
        Client.__id += 1

        self.tcpProtocol = None
        self.tcpServer = tcpServer

        # attributes for file transfer:
        self.currentFilePath = None
        self.currentFile = None
        self.currentMD5 = None

        #logging
        self.logger = logging.getLogger("PySchedServer")

    def assignTcpProtocol(self, tcpProtocol):
        '''
        @summary: Assigns the given TcpProtocol to this client.
        @param tcpProtocol: The TcpProtocol
        @result:
        '''
        self.tcpProtocol = tcpProtocol;

    def connectionEstablished(self):
        '''
        @summary: Is called when the tcp connection is established
        @result:
        '''
        self.tcpServer.connectionMade(self)

    def connectionLost(self, reason):
        '''
        @summary: Is called when the network connection is lost
        @param reason: Reason for the connection lost
        @result:
        '''
        self.tcpServer.connectionLost(self)

    def lineReceived(self, line):
        '''
        @summary: Is called when a line is received.
        @param line: The received line
        @result:
        '''
        cmd = json.loads(line, encoding="ISO-8859-1")
        networkCommand = cmd.get("nCommand", "")

        if networkCommand == "heartbeat":
            cmd = json.dumps({"nCommand": "heartBeatResponse"})
            self.sendMessage(cmd)
            return

        self.tcpServer.commandReceived(self, line)

    def sendMessage(self, message):
        '''
        @summary: Sends a message to the client.
        @param message: The message to send
        @result:
        '''
        self.tcpProtocol.sendMessage(message)
