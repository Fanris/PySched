# -*- coding: utf-8 -*-
'''
Created on 2013-01-11 14:45
@summary:
@author: Martin Predki
'''

from PySched.Common.Interfaces.Network.MessageHandlerInterface import MessageHandlerInterface
from PySched.Common.Communication.CommandBuilder import CommandBuilder
from PySched.Common.DataStructures import JobState, Program
from PySched.Common.IO import FileUtils

import json
import logging

class MessageHandler(MessageHandlerInterface):
    '''
    @summary: Handler class for all network messages
    '''
    def __init__(self, pySchedServer):
        '''
        @summary:           Initializes the message handler
        @param pySchedServer: a reference to the PySchedServer
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
        self.pySchedServer = pySchedServer

    def messageReceived(self, networkId, message):
        '''
        @summary:           Should be called if a new message is received.
        @param networkId:   An identifier for the sender of the message
        @param command:     the received message
        @result:
        '''
        self.logger.debug("Message received: {}".format(message))
        commandDict = json.loads(message)

        # Run command....
        cmd = commandDict.get("command", None)

        if cmd and hasattr(self, commandDict.get("command", None)):
            getattr(self, commandDict.get("command", None))(networkId, commandDict)
        else:
            self.logger.warning("Cannot parse command: {}".format(message))


    def connectionLost(self, networkId):
        '''
        @summary:           Is called if a network connection is closed.
        @param networkId:   The id of the client who closed the connection.
        @result:
        '''
        self.pySchedServer.removeWorkstation(networkId)

    def workstationInfo(self, networkId, info):
        '''
        @summary:           Is called if new Informations of a workstation
                            are available
        @param networkId:   Global id of the sender (workstation)
        @param info:        A dictionary containing all (new) informations
                            of the workstation
        @result:
        '''
        self.pySchedServer.updateWorkstation(networkId, info)

    def jobInfo(self, networkId, jobState):
        '''
        @summary:           Is called if a job is finished.
        @param networkId:   global id of the workstation which sent this message
        @param jobState:    dictionary containing the job informations
        @result:
        '''
        self.pySchedServer.updateJobState(jobState)

    def addJob(self, networkId, jobInfo):
        '''
        @summary:           Is called when a new should be added.
        @param networkId:   global id of the sender
        @param jobInfo:     dictionary containing the jobInformation
        @result:
        '''
        job = self.pySchedServer.addJob(jobInfo)

        if job:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, jobId=job.jobId))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def schedule(self, networkId, data):
        '''
        @summary:           Is called when th scheduler should be forced to
                            schedule. Mainly for debug purpose
        @param networkId:   global client id
        @result:
        '''
        self.pySchedServer.schedule()

    def checkJobs(self, networkId, data):
        '''
        @summary:           Is called when the jobs should be updated
        @param networkId:   global client id
        @result:
        '''
        self.pySchedServer.checkJobs()

    def killJob(self, networkId, data):
        '''
        @summary:           Is called when a kill signal is received.
        @param networkId:   global client id
        @param data:        Dictionary containing the userId and the job id
        @result:
        '''
        self.pySchedServer.killJob(data.get("jobId", None), data.get("userId", None))
        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))

    def getJobs(self, networkId, data):
        '''
        @summary:           is called when a user requested a list of his jobs.
        @param networkId:   global id of the client
        @param data:        dictionary containing the userId and the showAll 
                            flag
        @result:
        '''
        userId = data.get("userId", None)
        showAll = data.get("showAll", False)
        showAllUser = data.get("showAllUser", False)

        self.logger.debug("Get Jobs for user ({}, showAll={})".format(userId, showAll))
        jobs = self.pySchedServer.getJobList(userId, showAll, showAllUser)

        if not jobs:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return False

        jobList = []
        for job in jobs:
            job.userId = self.pySchedServer.lookupUserId(job.userId).userId
            job.stateId = JobState.lookup(job.stateId)
            jobList.append(job.__dict__)

        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, jobs=jobList))
        return True

    def archiveJob(self, networkId, data):
        '''
        @summary:           Is called when an user requests to archive a job
        @param networkId:   global client id
        @param data:        Dictionary containing the userId and the jobId
        @result:
        '''
        self.pySchedServer.archiveJob(data["jobId"], data["userId"])

    def getResults(self, networkId, data):
        '''
        @summary:           Is called when an user requests the results of a job
        @param networkId:   global client id
        @param data:        A dictionary containig userId and jobId
        @result:
        '''
        userId = data.get("userId", None)
        jobId = data.get("jobId", None)

        resultsFile = self.pySchedServer.returnResultsToClient(userId, jobId)

        if not resultsFile:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return False

        self.logger.info("Sending results...")
        if not self.pySchedServer.networkManager.sendFile(networkId, resultsFile):
            self.logger.error("Could not transfer file {} to {}".format(resultsFile, networkId))
            FileUtils.deleteFile(resultsFile)
            return False

        FileUtils.deleteFile(resultsFile)
        self.pySchedServer.archiveJob(jobId)
        return True

    def createUser(self, networkId, userInfo):
        '''
        @summary:           Is called when a new user should be created.
        @param userInfo:    a dictionary containing the user informations
        @result:            Returns the generated user name of the user.
        '''
        userId = userInfo.get("userId", None)
        try:
            del userInfo["userId"]
        except:
            pass

        if self.pySchedServer.createUser(userId, userInfo):
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, message="User created."))

        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def getUsers(self, networkId, data):
        '''
        @summary:           Is called when a client request a list of all registered users
        @param networkId:   The networkId of the client
        @param data:        The current userId of the client
        @result: 
        '''
        users = self.pySchedServer.getUsers(data.get("userId", None))

        if users:
            userList = []
            for user in users:
                userList.append(user.__dict__)

            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, users=userList))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def deleteUser(self, networkId, data):
        '''
        @summary:           Deletes a user
        @param networkId:   the networkId of the sender
        @param data:        userId of the requesting user, email of the user 
                            which should be deleted
        @result: 
        '''
        userId = data.get("userId", None)
        email = data.get("email", None)

        if self.pySchedServer.deleteUser(userId, email):
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def getPrograms(self, networkId, data):
        '''
        @summary:           Is called when a client requests a list of all 
                            available Programs.
        @param networkId:   The client which sends the request.
        @param data:
        @result:
        '''
        programs = self.pySchedServer.getFromDatabase(Program)

        programList = []
        for program in programs:
            programList.append(program.__dict__)

        self.pySchedServer.networkManager.sendMessage(
            networkId, 
            CommandBuilder.buildResponseString(result=True, programs=programList))

    def addProgram(self, networkId, data):
        '''
        @summary:           Is called when a new program should be added to 
                            the database
        @param networkId:
        @param data:
        @result: 
        '''
        user = data.get("userId")
        program = Program()
        program.programName = data.get("programName", None)
        program.programExec = data.get("programExec", None)
        program.programPath = data.get("programPath", None)
        program.programVersion = data.get("programVersion", None)

        if self.pySchedServer.addProgram(user, program):
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=True))

    def deleteProgram(self, networkId, data):
        '''
        @summary:           Deletes the program with the given name form the 
                            database
        @param networkId:
        @param data:        userId, programName
        @result: 
        '''
        userId = data.get("userId", None)
        programName = data.get("programName", None)

        if self.pySchedServer.deleteProgram(userId, programName):
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=True))
        else:
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=False))


    def getWorkstations(self, networkId, data):
        workstations = self.pySchedServer.workstations
        server = self.pySchedServer.getServerInformations()

        self.pySchedServer.networkManager.sendMessage(
            networkId, 
            CommandBuilder.buildResponseString(
                result=True, 
                workstations=workstations.values(), 
                server=server))

    def deleteJob(self, networkId, data):
        '''
        @summary:           Is called when a client requests to delete a job.
        @param networkId:   the client which sends the request
        @param data:        userId, jobId
        @result:
        '''
        if self.pySchedServer.deleteJob(data.get("userId", ""), data.get("jobId", None)):
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))

    def checkUser(self, networkId, data):
        '''
        @summary:           Is called when a UI is connected. Retrieves the 
                            user informations.
        @param networkId:   the sender of the request.
        @param data:        contains the userId to check
        @result: 
        '''
        user = self.pySchedServer.getUser(data.get("userId", None))

        if not user:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return

        if user.admin:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, admin=True))
        else:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))

    def shutdown(self, networkId, data):
        '''
        @summary:           Shuts the server down, if the user has admin-
                            privileges
        @param networkId:   the sender of the request
        @param data:        the userId
        @result: 
        '''
        user = self.pySchedServer.getUser(data.get("userId", None))
        
        if not user or not user.admin:
            self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=False))
            return
        
        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True))
        self.pySchedServer.shutdown()

    def getJobLog(self, networkId, data):
        '''
        @summary:           Returns the logfile of a Job to the user.
        @param networkId:  the sender who send the request
        @param data:        jobId, username
        @result:
        '''
        log = self.pySchedServer.getLog(data.get("jobId", None), data.get("userId", None))
        self.pySchedServer.networkManager.sendMessage(networkId, CommandBuilder.buildResponseString(result=True, log=log))

    def addPath(self, networkId, data):
        '''
        @summary:           Appends a new search Path for programs at the 
                            workstations
        @param networkId:   The sender
        @param data:        userId, path
        @result: 
        '''
        userId = data.get("userId", None)
        path = data.get("path", None)

        if userId and path:
            self.pySchedServer.appendPath(userId, path)

    def getPaths(self, networkId, data):
        '''
        @summary:           Returns the current configured program search Paths
        @param networkId:
        @param data:        userId
        @result: 
        '''

        user = self.pySchedServer.getUser(data.get("userId", None))
        if user.admin:
            paths = self.pySchedServer.getPath()
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(
                    result=True,
                    paths=paths))
            return True
        self.pySchedServer.networkManager.sendMessage(
            networkId,
            CommandBuilder.buildResponseString(
                result=False))

    def shutdownAll(self, networkId, data):
        '''
        @summary:           Shuts the server and all workstations down
        @param networkId:
        @param data:        userId
        @result: 
        '''
        self.pySchedServer.stopAll(data.get("userId", None))

    def shutdownWorkstation(self, networkId, data):
        '''
        @summary:           Shuts down the given Workstation
        @param networkId:   
        @param data:        userId, workstationName
        @result: 
        '''
        if self.pySchedServer.stopWorkstation(
            data.get("userId", None),
            data.get("workstationName", None)):
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=True))
        else:
            self.pySchedServer.networkManager.sendMessage(
                networkId, 
                CommandBuilder.buildResponseString(result=False))


    def pauseJob(self, networkId, data):
        '''
        @summary:           Pauses the job with the given jobId
        @param networkId:
        @param data:        userId, jobId
        @result: 
        '''
        user = data.get("userId", None)
        jobId = data.get("jobId", None)

        self.pySchedServer.pauseJob(user, jobId)

    def resumeJob(self, networkId, data):
        '''
        @summary:           Resumes the job with the given jobId
        @param networkId:
        @param data:        userId, jobId
        @result: 
        '''        
        user = data.get("userId", None)
        jobId = data.get("jobId", None)

        self.pySchedServer.resumeJob(user, jobId)

    def requestFileDownload(self, networkId, data):
        '''
        @summary:           Is called, when a client requests a results file
        @param networkId:   The client which sends the request
        @param data:        userId, jobId
        @result: 
        '''
        userId = data.get("userId", None)
        jobId = data.get("jobId", None)

        pathToResultFile = self.pySchedServer.returnResultsToClient(userId, jobId)
        if pathToResultFile:
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=True, path=pathToResultFile))
        else:
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=False))

    def fileDownloadCompleted(self, networkId, data):
        pathToFile = data.get("path", None)
        jobId = data.get("jobId", None)

        FileUtils.deleteFile(pathToFile)
        self.pySchedServer.archiveJob(jobId)
        return True

    def requestFileUpload(self, networkId, data):
        '''
        @summary:           Is called by a client when a file should be transferred
                            to the server.
        @param networkId:   The id of the requesting client.
        @param data:        jobId
        @result: 
        '''
        jobId = data.get("jobId", None)
        pathToUpload = self.pySchedServer.getUploadPath(jobId)

        if pathToUpload:
            self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildUploadPathString(
                    pathToUpload, jobId))

    def fileUploadCompleted(self, networkId, data):
        '''
        @summary:           Is called when a file upload is completed 
        @param networkId:   The client which sends the file.
        @param data:        jobId, path
        @result: 
        '''
        jobId = data.get("jobId", None)
        pathToFile = data.get("path", None)

        if jobId and pathToFile:
            self.pySchedServer.fileReceived(pathToFile, jobId=jobId)

        self.pySchedServer.networkManager.sendMessage(
                networkId,
                CommandBuilder.buildResponseString(result=True))


