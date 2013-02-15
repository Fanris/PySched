# -*- coding: utf-8 -*-
'''
Created on 2013-01-15 12:21
@summary:
@author: Martin Predki
'''

from PySchedUI.Common import readBytesFromFile
from SSHTunnel import SSHTunnel

import socket
import struct
import json
import os
import base64

import logging

class Network(object):
    '''
    @summary: PySchedUI Network class
    '''
    def __init__(self, pySchedUI, debug=False, keyFile=None):
        self.logger = logging.getLogger("PySchedUI")
        self.pySchedUI = pySchedUI
        self.connection = None
        self.receivedData = ""
        self.debug = debug
        self.keyFile = keyFile
        self.sshTunnel = None

    def sendCommand(self, command, waitForResponse=True, dryRun=False, **kwargs):
        cmd = {"command": command}
        for key, value in kwargs.iteritems():
            cmd[key] = value

        message = json.dumps(cmd) + "\r\n"
        if dryRun:
            self.logger.info("Dry Run! Would now send message: {}".format(message))
            return True

        self.connection.send(message)

        if waitForResponse:
            return self.listen()
        else:
            return None

    def sendFile(self, path):
        '''
        @summary: Sends the given file to the workstation
        @param pathToFile: Path to the file
        @param jobId: Job id to which this file belongs
        @result:
        '''
        filename = os.path.split(path)[1]
        self.sendCommand("", waitForResponse=False, nCommand="put", filename=filename, md5="")

        for bytes in readBytesFromFile(path):
            self.sendCommand("", waitForResponse=False, nCommand="file", chunk=base64.b64encode(bytes))

        return self.sendCommand("", waitForResponse=True, nCommand="fileOk")

    def getFile(self, path):
        '''
        @summary: Is called after a file is requested. This function receives and stores
        the file
        @param path: Path where the file should be stored.
        @result:
        '''
        returnValue = self.listen()

        with open(path, "w") as f:
            while returnValue.get("nCommand", False) == "file":
                chunk = base64.b64decode(returnValue.get("chunk", ""))
                f.write(chunk)
                returnValue = self.listen()
        return True

    def listen(self):
        while True:
            # New line signals a command.
            if "\r\n" in self.receivedData:
                # Split the received Data in an command chunk and the rest.
                (commandDict, leftover) = self.receivedData.split('\r\n', 1)
                self.logger.debug("new data: {}".format(commandDict))

                # Save the leftover in the receivedData
                self.receivedData = leftover

                # parse the command dict to a python dictionary
                commandDict = json.loads(commandDict)

                # break the listen loop
                return commandDict
            else:
                self.receivedData += self.connection.recv(1024)
                #self.logger.debug("Received Data: {}".format(self.receivedData))


    def openConnection(self, timeout=5):
        multiGroup = "228.0.0.5"
        udpPort = 50000
        tcpPort = 49999

        # Join multicast group

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.bind(('', udpPort))
        sock.settimeout(timeout)

        group = socket.inet_aton(multiGroup)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.logger.info("Searching for a PySchedServer...")
        sock.sendto('{"nCommand": "ping"}', (multiGroup, udpPort))

        msg = ""
        while True:
            try:
                (msg, address) = sock.recvfrom(1024)
                if "serverAvailable" in msg:
                    commandDict = json.loads(msg)
                    if commandDict["nCommand"] == "serverAvailable":
                        self.logger.info("PySchedServer found.")
                        sock.close()
                        break
            except socket.timeout:
                self.logger.info("No PySched Server available!")
                return None

        try:
            self.logger.info("Building up connection...")
            ip = address[0]
            self.sshTunnel = SSHTunnel(keyFile=self.keyFile, host=ip)
            if self.sshTunnel.buildTunnel():
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                s.connect(('localhost', tcpPort))
                self.connection = s
                self.logger.info("Connection established.")
                return True

        except Exception, e:
            raise e

        return False

    def closeConnection(self):
        self.connection.close()

