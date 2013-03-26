# -*- coding: utf-8 -*-
'''
Created on 2013-02-13 13:02
@summary: Builds an ssh tunnel to the server.
@author: Martin Predki
'''

import select
import SocketServer
import logging
import thread

import paramiko
import random
import socket

SSH_PORT = 22

class SSHTunnel(object):
    '''
    @summary: Main class of the tunnel service.
    '''
    def __init__(self, keyFile="", username="pysched", portRange=(1024, 49999),
        host=None, hostPort=49999):
        '''
        @summary: Initializes the Tunnel service
        @param username: the username for the ssh connection (Default: pysched)
        @param keyFile: the private key for the user.
        @param port: the port to tunnel from (local-side, default: 49999)
        @result:
        '''
        self.logger = logging.getLogger("PySchedClient")
        self.user = username
        self.keyFile = keyFile
        self.portRange = portRange
        self.port = random.randint(self.portRange[0], self.portRange[1])
        self.host = host
        self.hostPort = hostPort

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())

        self.serve = True
        self.isConnected = False

    def buildTunnel(self):
        '''
        @summary: Builds the SSH tunnel.
        @result:
        '''
        self.logger.info("Build up SSH-Tunnel...")
        try:
            retryCount = 0
            self.serve = True

            self.logger.debug("Connect to: {}:{} with username {}".\
                format(self.host, SSH_PORT, self.user))

            while retryCount < 5:
                try:
                    self.client.connect(self.host, SSH_PORT, username=self.user,
                        key_filename=self.keyFile)

                    self.logger.debug("Connect ForwardServer {}:{}:{}".\
                        format(self.port, self.host, self.hostPort))

                    self.forwardServer = self.createForwardServer(
                        self.port,
                        self.host,
                        self.hostPort,
                        self.client.get_transport(),
                        self)

                    thread.start_new_thread(self.forwardServer.serve_forever, ())
                    self.isConnected = True
                    return self.port
                except socket.error:
                    retryCount += 1
                    self.port = random.randint(self.portRange[0], self.portRange[1])
            self.logger.error("Failed to build up a SSH connection.")
            return False

        except Exception, e:
            self.logger.error("Could not connect to server! Reason: {}".
                format(e))

    def closeTunnel(self):
        '''
        @summary: Closes the ssh tunnel
        @result:
        '''
        self.serve = False


    def createForwardServer(self, localPort, remoteHost,
        remotePort, transport, sshClient):
        '''
        @summary: Creates a Subhandler for the Forward Tunnel. This is kind of a
        hack because there is no other way to give the Handler access to the server
        attributes
        @param localPort: The localPort to listen on
        @param remoteHost: the remote host ip
        @param remotePort: the remote host port
        @param transport: the transport layer
        @param sshClient: a reference to the ssh client class
        @result:
        '''
        class SubHandler(Handler):
            chain_host = remoteHost
            chain_port = remotePort
            ssh_transport = transport
            ssh_Client = sshClient

        # Open forward tunnel
        return ForwardServer(('', localPort), SubHandler)

class ForwardServer (SocketServer.ThreadingTCPServer):
    '''
    @summary: Threaded TCPServer
    '''
    daemon_threads = True
    allow_reuse_address = True

class Handler (SocketServer.BaseRequestHandler):
    '''
    @summary: Socket Handler
    '''
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host,
                                                    self.chain_port),
                                                    self.request.getpeername())
        except Exception:
            return

        if chan is None:
            return

        self.ssh_Client.logger.debug("Starting ssh loop")
        while self.ssh_Client.serve:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                chan.send(data)

            if chan in r:
                data = chan.recv(1024)
                self.request.send(data)

        self.ssh_Client.logger.info("Closing SSH-Tunnel.")
        chan.close()
        self.request.close()
