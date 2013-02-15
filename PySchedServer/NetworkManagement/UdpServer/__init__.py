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

class UdpServer(object):
    '''
    @summary: UDP Server class
    '''

    def __init__(self, port, multicastGroup):
        '''
        @summary: Initializes the udp server
        @param port: The port on which the server should listen
        @param multicastGroup: The multicastGroup to which the server should be connected
        @param pySchedServer: A reference to the PySchedServer
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
        self.port = port
        self.multicastGroup = multicastGroup
        self.protocol = UdpProtocol(self)

    def startServer(self):
        '''
        @summary: Starts the server
        @result:
        '''
        reactor.listenMulticast(self.port, self.protocol, listenMultiple=True)
        return True

    def stopServer(self):
        pass

    def sendServerAvailableBroadcast(self):
        '''
        @summary: Sends a "Server available" Broadcast
        @result:
        '''
        self.logger.info("Send server available...")
        # creating command
        msg = json.dumps({"nCommand": "serverAvailable"})
        self.protocol.sendBroadcast(msg)

    def messageReceived(self, message, host):
        '''
        @summary: Checks if the received command is used for the networkManager or
        pass it to the messageReceiver
        @param client: the origin of the command
        @param command: the command
        @result:
        '''
        self.logger.debug("Broadcast received: {}".format(message))
        try:
            cmd = json.loads(message)
            c = cmd.get("nCommand", None)

            if not c:
                return

            if c == "ping":
                self.sendServerAvailableBroadcast()
        except:
            pass

