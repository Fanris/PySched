# -*- coding: utf-8 -*-
'''
Created on 2013-01-11 14:45
@summary:
@author: Martin Predki
'''

from PySched.Common.Interfaces.Network.MessageHandlerInterface import MessageHandlerInterface
from PySched.Common.Communication.CommandBuilder import CommandBuilder
from PySched.Common.DataStructures import JobState, Compiler
from PySched.Common.IO import FileUtils

import json
import logging

class MessageHandler(MessageHandlerInterface):
    '''
    @summary: Handler class for all network messages
    '''
    def __init__(self, pySchedServer):
        '''
        @summary: Initializes the message handler
        @param pySchedServer: a reference to the PySchedServer
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
        self.pySchedServer = pySchedServer

    def messageReceived(self, sender, message):
        '''
        @summary: Should be called if a new message is received.
        @param sender: An identifier for the sender of the message
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


    def connectionLost(self, networkId):
        '''
        @summary: Is called if a network connection is closed.
        @param networkId: The id of the client who closed the connection.
        @result:
        '''
        self.pySchedServer.removeWorkstation(networkId)

    def connectionMade(self, networkId):
        pass

    def workstationInfo(self, networkId, info):
        '''
        @summary: Is called if new Informations of a workstation
        are available
        @param networkId: Global id of the sender (workstation)
        @param info: A dictionary containing all (new) informations
        of the workstation
        @result:
        '''
        self.pySchedServer.updateWorkstation(networkId, info)

    def jobInfo(self, networkId, jobState):
        '''
        @summary: Is called if a job is finished.
        @param networkId: global id of the workstation which sent this message
        @param jobState: dictionary containing the job informations
        @result:
        '''
        self.pySchedServer.updateJobState(jobState)

    def addJob(self, networkId, jobInformation):
        '''
        @summary: Is called when a new should be added.
        @param networkId: global id of the sender
        @param jobInformation: dictionary containing the jobInformation
        @result:
        '''
        job = self.pySchedServer.addJob(jobInformation)

        if job:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, jobId=job.jobId))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def schedule(self, networkId, data):
        '''
        @summary: Is called when th scheduler should be forced to
        schedule. Mainly for debug purpose
        @param networkId: global client id
        @result:
        '''
        self.pySchedServer.schedule()

    def checkJobs(self, networkId, data):
        '''
        @summary: Is called when the jobs should be updated
        @param networkId: global client id
        @result:
        '''
        self.pySchedServer.checkJobs()

    def killJob(self, networkId, data):
        '''
        @summary: Is called when a kill signal is received.
        @param networkId: global client id
        @param data: Dictionary containing the userId and the job id
        @result:
        '''
        self.pySchedServer.killJob(data.get("jobId", None), data.get("username", None))
        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))

    def getJobs(self, networkId, data):
        '''
        @summary: is called when a user requested a list of his jobs.
        @param networkId: global id of the client
        @param data: dictionary containing the username and the showAll flag
        @result:
        '''
        username = data["username"]
        showAll = data["showAll"]

        self.logger.debug("Get Jobs for user ({}, showAll={})".format(username, showAll))
        jobs = self.pySchedServer.getJobList(username, showAll)

        if not jobs:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return False

        jobList = []
        for job in jobs:
            job.stateId = JobState.lookup(job.stateId)
            jobList.append(job.__dict__)

        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, jobs=jobList))
        return True

    def archiveJob(self, networkId, data):
        '''
        @summary: Is called when an user requests to archive a job
        @param networkId: global client id
        @param data: Dictionary containing the username and the jobId
        @result:
        '''
        self.pySchedServer.archiveJob(data["jobId"], data["username"])

    def getResults(self, networkId, data):
        '''
        @summary: Is called when an user requests the results of a job
        @param networkId: global client id
        @param jobId: id of the job
        @param userId: id of the user who sent the request
        @result:
        '''
        username = data.get("username", None)
        jobId = data.get("jobId", None)

        resultsFile = self.pySchedServer.returnResultsToClient(username, jobId)

        if not resultsFile:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return False

        self.logger.info("Sending results...")
        if not self.pySchedServer.networkManager.sendFile(networkId, resultsFile):
            self.logger.error("Could not transfer file {} to {}".format(resultsFile, networkId))
            FileUtils.deleteFile(resultsFile)
            return False

        FileUtils.deleteFile(resultsFile)
        return True

    def createUser(self, networkId, userInformations):
        '''
        @summary: Is called when a new user should be created.
        @param userInformations: a dictionary containing the user informations
        @result: Returns the generated user name of the user.
        '''
        if self.pySchedServer.createUser(userInformations):
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, message="User created."))

        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def fileTransferCompleted(self, networkId, pathToFile):
        '''
        @summary: Is called when a file transfer is completed.
        @param networkId: The id of the client which receives the file
        @param networkFileObject: a network file object.
        @result:
        '''
        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))
        self.pySchedServer.fileReceived(pathToFile)

    def fileTransferFailed(self, networkId, pathToFile):
        '''
        @summary: Is called when a file transfer is completed.
        @param networkId: The id of the client which receives the file
        @param networkFileObject: a network file object.
        @result:
        '''
        self.pySchedServer.fileTransferFailed(pathToFile)
        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def getCompiler(self, networkId, data):
        '''
        @summary: Is called when a client requests a list of all available Compilers.
        @param networkId: The client which sends the request.
        @param data:
        @result:
        '''
        compiler = self.pySchedServer.getFromDatabase(Compiler)

        if not compiler:
            compiler = []

        if isinstance(compiler, Compiler):
            compiler = [compiler]

        for index in range(0, len(compiler)):
            compiler[index] = compiler[index].__dict__

        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, compiler=compiler))


    def getParser(self, networkId, data):
        '''
        @summary: Is called when a client requests a list of all available Parsers.
        @param networkId: The client which sends the request.
        @param data:
        @result:
        '''
        pass

    def getWorkstations(self, networkId, data):
        workstations = self.pySchedServer.workstations

        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, workstations=workstations.values()))

    def deleteJob(self, networkId, data):
        '''
        @summary: Is called when a client requests to delete a job.
        @param networkId: the client which sends the request
        @param data: username, jobId
        @result:
        '''
        if self.pySchedServer.deleteJob(data.get("username", ""), data.get("jobId", None)):
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def checkUser(self, networkId, data):
        '''
        @summary: Is called when a UI is connected. Retrieves the user informations.
        @param networkId: the sender of the request.
        @param data: contains the username to check
        @result: 
        '''
        user = self.pySchedServer.getUser(data.get("username", None))

        if not user:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return

        if user.admin:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, admin=True))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))
