# -*- coding: utf-8 -*-
'''
Created on 2012-11-30 13:35
@summary:
@author: Maritn Predki
'''

from twisted.internet import reactor

from UdpProtocol import UdpProtocol

import json
import logging

class UdpClient(object):
    '''
    @summary: UDP Server class
    '''

    def __init__(self, port, multicastGroup, networkManager):
        '''
        @summary: Initializes the udp server
        @param port: The port on which the server should listen
        @param multicastGroup: The multicastGroup to which the server should be connected
        @param pySchedClient: A reference to the pySchedClient
        @result:
        '''
        self.logger = logging.getLogger("NetworkManagementClient")
        self.port = port
        self.multicastGroup = multicastGroup
        self.protocol = UdpProtocol(self)
        self.networkManager = networkManager
        self.listener = None

    def startClient(self):
        '''
        @summary: Starts the server
        @result:
        '''
        self.logger.info("UDP Listener started on port {}".format(self.port))
        self.listener = reactor.listenMulticast(self.port, self.protocol, listenMultiple=True)

    def stopClient(self):
        if self.listener:
            self.listener.stopListening()
            self.logger.info("UDP Listener stopped.")

    def sendPing(self):
        '''
        @summary: Broadcasts a ping to the multigroup, looking for a server
        @result:
        '''
        self.logger.info("Searching for Server...")
        # Creating ping command
        msg = json.dumps({ "nCommand": "ping"})
        self.protocol.sendBroadcast(msg)

    def messageReceived(self, message, host):
        '''
        @summary: Checks if the received command is used for the networkManager or
        pass it to the messageReceiver
        @param client: the origin of the command
        @param command: the command
        @result:
        '''
        try:
            cmd = json.loads(message)
            c = cmd.get("nCommand", None)

            if not c:
                return

            if c == "serverAvailable":
                self.logger.info("Server available. Building the tcp connection.")
                self.networkManager.serverFound(host)
        except:
            pass
