# -*- coding: utf-8 -*-
'''
Created on 2013-01-09 14:57
@summary:
@author: Martin Predki
'''

class NetworkInterface(object):
    '''
    @summary: This class is used by the PySchedServer / Client as an interface to the network
    module. The class imported by the PySchedServer / Client must implement this functions.
    '''
    def __init__(self, workingDir, messageReceiver, rsaPath=None):
        '''
        @summary: Is called to Initialize the networkInterface
        @param workingDir: a Path to a directory which can be used to store network specific data if needed.
        @param messageReceiver: The messageReceiver is the PySched-side network interface which exposes
        functions to parse received messages. See Common.Interfaces.Network.MessageReceiver for further informations.
        @result:
        '''
        self.workingDir = workingDir
        self.messageReceiver = messageReceiver
        self.pathToRsa = rsaPath

    def startService(self):
        '''
        @summary: Is called when the network connection(s) should be opened
        @result:
        '''
        raise NotImplementedError

    def stopService(self):
        '''
        @summary: Is called when the network connection(s) should be closed.
        @result:
        '''
        raise NotImplementedError

    def sendMessage(self, receiver, message):
        '''
        @summary: Sends a Message
        @param receiver: the receiver of the message
        @param message: the message
        @result:
        '''
        raise NotImplementedError

    def sendFile(self, localPath, remotePath, callback):
        '''
        @summary: Sends a File
        @param receiver: the receiver of the file
        @param pathToFile: the path to the file
        @result: Returns True if the file was send
        '''
        raise NotImplementedError

    def getFile(self, localPath, remotePath, callback):
        '''
        @summary: Sends a File
        @param receiver: the receiver of the file
        @param pathToFile: the path to the file
        @result: Returns True if the file was send
        '''
        raise NotImplementedError
