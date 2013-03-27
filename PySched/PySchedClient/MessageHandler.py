# -*- coding: utf-8 -*-
'''
Created on 2013-01-09 15:51
@summary:
@author: Martin Predki
'''

from PySched.Common.Interfaces.Network.MessageHandlerInterface import MessageHandlerInterface

import json
import logging

class MessageHandler(MessageHandlerInterface):
    '''
    @summary: Handles all incoming network messages.
    '''
    def __init__(self, pySchedClient):
        '''
        @summary:       Initializes the Handler
        @param pySchedClient: A reference to the PySchedClient.
        @result:
        '''
        self.logger = logging.getLogger("PySchedClient")
        self.pySchedClient = pySchedClient

    def messageReceived(self, sender, message):
        '''
        @summary:       Should be called if a new message is received.
        @param sender:  An identifier for the sender of the message
        @param command: the received message
        @result:
        '''
        self.logger.debug("Message received: {}".format(message))
        commandDict = json.loads(message)

        # Run command....
        cmd = commandDict.get("command", None)

        if cmd and hasattr(self, commandDict.get("command", None)):
            getattr(self, commandDict.get("command", None))(sender, commandDict)
        else:
            self.logger.warning("Cannot parse command: {}".format(message))

    def connectionBuild(self, sender):
        '''
        @summary:       Is called if the server connection is established.
        @result:
        '''
        self.pySchedClient.serverId = sender
        self.pySchedClient.startWorkstationStateLoop()

    def connectionLost(self, sender):
        '''
        @summary:       Is called if the server connection is lost.
        @result:
        '''
        self.pySchedClient.serverId = None
        self.pySchedClient.stopWorkstationStateLoop()

    def addJob(self, client, data):
        '''
        @summary:       Is called, when a job is received.
        @result:
        '''
        self.pySchedClient.addJob(data)

    def getResults(self, client, data):
        '''
        @summary:       Is called, when the job results are requested.
        @result:
        '''
        self.pySchedClient.returnResults(data.get("jobId", None))

    def getJobState(self, client, data):
        '''
        @summary:       Is called, when a job state is requested.
        @result:
        '''
        self.pySchedClient.returnJobState(data.get("jobId", None))

    def killJob(self, client, data):
        '''
        @summary:       Is called, when a job should be aborted.
        @result:
        '''
        self.pySchedClient.abortJob(data.get("jobId", None))

    def fileTransferCompleted(self, sender, pathToFile):
        '''
        @summary:       Is called when a file transfer is completed.
        @param sender:  The id of the client which receives the file
        @param pathToFile: Path to the file.
        @result:
        '''
        self.pySchedClient.fileReceived(pathToFile)

    def put(self, client, data):
        '''
        @summary:       Global Command. Signals that a file is to be received.
        @param data:    A dictionary containing the jobId, filename and 
                        md5Hashsum
        '''
        self.pySchedClient.incomingFiles.append( {"filename": data.get("filename", None), "jobId": data.get("jobId", None)} )

    def checkForPrograms(self, sender, data):
        '''
        @summary:       Client command. Causes the sender to if a list of 
                        programs is installed.
        @param sender:  the sender of the command.
        @param data:    the data dictionary contains a key ("programs")
                        which consists of a list of dictionaries. Each 
                        dictionary contains a key "programName" and a key 
                        "programExec". The programName defines the readable 
                        Name of the program and programExec defines the 
                        programs executable to check for.
        @result:
        '''
        self.logger.debug("Check programs...")
        self.pySchedClient.checkForPrograms(data.get("programs", []))

    def shutdown(self, sender, data=None):
        '''
        @summary:       Shuts the Workstation down.
        @param sender:  the sender of the command
        @param data:    empty
        @result: 
        '''
        self.pySchedClient.shutdown()
