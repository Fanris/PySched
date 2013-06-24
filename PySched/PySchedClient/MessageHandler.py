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
        @summary:       Is called when the server requests the job results
        @param client:  
        @param data:    jobId, path
        @result: 
        '''
        jobId = data.get("jobId", None)
        remotePath = data.get("path", None)
        self.pySchedClient.returnResults(jobId, remotePath)

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

    def pauseJob(self, client, data):
        '''
        @summary:       Is called, when a job should be paused.
        @result:
        '''
        self.pySchedClient.pauseJob(data.get("jobId", None))

    def updateJob(self, client, data):
        '''
        @summary:       Is called, when a job should be updated
        @param client:  
        @param data:    jobId, path
        @result: 
        '''
        userId = data.get("userId", None)
        path = data.get("path", None)
        self.pySchedClient.updateJobData(userId, path)


    def resumeJob(self, client, data):
        '''
        @summary:       Is called, when a job should be paused.
        @result:
        '''
        self.pySchedClient.resumeJob(data.get("jobId", None))

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

    def reserveCPU(self, sender, data):
        '''
        @summary:       Client command. Causes the receiver to reserve a 
                        CPU for a job.
        @param sender:  The sender of the command
        @param data:    The data contains only a key "jobId" which specifies
                        the job, for which the cpu is reserved.
        @result: 
        '''
        jobId = data.get("jobId", None)
        self.pySchedClient.reserveCPU(jobId)

    def shutdown(self, sender, data=None):
        '''
        @summary:       Shuts the Workstation down.
        @param sender:  the sender of the command
        @param data:    empty
        @result: 
        '''
        self.pySchedClient.shutdown()

    def updatePath(self, sender, data):
        '''
        @summary:       Updates the program path file
        @param sender:  the sender of the command
        @param data:
        @result: 
        '''
        self.pySchedClient.updatePath(data.get("path", None))

    def setMaintenance(self, sender, data):
        '''
        @summary:       Set or unset Maintenance status for this workstation
        @param sender:
        @param data:    maintenance
        @result: 
        '''
        self.pySchedClient.setMaintenance(data.get("maintenance", False))

    def getFileContent(self, sender, data):
        '''
        @summary:       Return the content of a given file.
        @param sender:  
        @param data:    jobId, path, sender (the client), lineCount
        @result: 
        '''
        jobId = data.get("jobId", None)
        path = data.get("path", None)
        sender = data.get("sender", None)
        lineCount = data.get("lineCount", 0)

        self.pySchedClient.getFileContent(jobId, path, lineCount, sender)

    def getJobDirStruct(self, sender, data):
        '''
        @summary:       Return the structure of a given job directory
        @param sender:  
        @param data:    jobId, sender (the client)
        @result: 
        '''
        jobId = data.get("jobId", None)
        sender = data.get("sender", None)

        self.pySchedClient.getJobDirStruct(jobId, sender)

    def updatePySched(self, sender, data):
        '''
        @summary:       Updates the software
        @param sender:
        @param data:
        @result: 
        '''
        self.pySchedClient.updatePySched()

