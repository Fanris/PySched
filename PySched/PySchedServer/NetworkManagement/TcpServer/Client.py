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

        if networkCommand == "put":
            self.logger.info("Receiving file...")
            self.receiveFile(cmd.get("filename", None), cmd.get("md5", None))
            return

        if networkCommand == "file":
            self.receiveFileChunk(cmd.get("chunk", None))
            return

        if networkCommand == "fileOk":
            self.logger.info("File received!")
            self.currentFile.close()
            self.tcpServer.fileTransferCompleted(self, self.currentFilePath, self.currentMD5)
            self.currentFilePath = None
            self.currentFile = None
            self.currentMD5 = None
            return

        if networkCommand == "heartbeat":
            cmd = json.dumps({"nCommand": "heartBeatResponse"})
            self.sendMessage(cmd)
            return

        self.tcpServer.commandReceived(self, line)

    def receiveFileChunk(self, chunk):
        '''
        @summary: Is called when a new file chunk is received.
        @param chunk: the new chunk
        @result:
        '''
        self.currentFile.write(base64.b64decode(chunk))

    def sendFile(self, path, md5):
        '''
        @summary: Sends the given file to the workstation
        @param pathToFile: Path to the file
        @param jobId: Job id to which this file belongs
        @result:
        '''
        filename = os.path.split(path)[1]
        cmd = json.dumps({"nCommand": "put", "filename": filename, "md5": md5})
        self.sendMessage(cmd)

        for bytes in readBytesFromFile(path):
            # Encoding the bytes to base64 String so it could be encoded
            # by json
            cmd = json.dumps({"nCommand": "file", "chunk": base64.b64encode(bytes)})
            self.sendMessage(cmd)

        cmd = json.dumps({"nCommand": "fileOk"})
        self.sendMessage(cmd)
        return True

    def sendMessage(self, message):
        '''
        @summary: Sends a message to the client.
        @param message: The message to send
        @result:
        '''
        self.tcpProtocol.sendMessage(message)

    def receiveFile(self, destination, md5):
        '''
        @summary: This function is called by the command parser if a file
        transfer is about to start (signaled by a put command)
        @param data: a dictionary containing informations about the file to receive
        @result:
        '''
        # Set the protocol to raw mode
        self.currentFilePath = os.path.join(self.tcpServer.networkManager.workingDir, destination)
        self.currentFile = open(self.currentFilePath, 'wb')
        self.currentMD5 = md5




