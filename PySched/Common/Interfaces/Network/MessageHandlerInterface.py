# -*- coding: utf-8 -*-
'''
Created on 2012-10-05 13:47
@summary: Class to parse received commands
@author: Martin Predki
'''
import json
import logging

class MessageHandlerInterface(object):
    '''
    @summary: This abstract class defines a function to parse a network message and exposes all commands
    that could be invoked by a network message or the network module
    '''

    def messageReceived(self, sender, message):
        '''
        @summary: Should be called if a new message is received.
        @param sender: An identifier for the sender of the message
        @param command: the received message
        @result:
        '''
        logging.debug("Message received: {}".format(message))
        commandDict = json.loads(message)

        # Run command....
        cmd = commandDict.get("command", None)

        if cmd and hasattr(self, commandDict.get("command", None)):
            getattr(self, commandDict.get("command", None))(sender, commandDict)
        else:
            logging.warning("Cannot parse command: {}".format(message))


    # Special Commands
    # ===============================================
    def connectionLost(self, sender, commandDict=None):
        '''
        @summary: Global Command. Signals that the given sender has lost the network connection.
        This command is generally called directly by a sender without a message.
        @param sender: The sender which lost the connection.
        @result:
        '''
        pass

    def connectionBuild(self, sender, commandDict=None):
        '''
        @summary: Global Command. Signals that a new sender has established a network connection
        @param sender: the new sender
        @param commandDict: None
        @result:
        '''
        pass

    def fileTransferCompleted(self, sender, pathToFile):
        '''
        @summary: Global Command. This function is called by the sender, when a file transfer is completed.
        @param sender: the sender which received the file
        @param pathToFile: Path to the file
        @result:
        '''
        pass

    def fileTransferFailed(self, sender, pathToFile):
        '''
        @summary: Global Command. This function is called by the sender, when a file transfer is completed.
        @param sender: the sender which received the file
        @param pathToFile: Path to the file
        @result:
        '''
        pass


    # Global Commands
    # ===============================================
    def msg(self, sender, data):
        '''
        @summary: Global Command. Prints an received Message
        @param data: dictionary containing at least a message value
        '''
        pass

    def put(self, sender, data):
        '''
        @summary: Global Command. Signals that a file is to be received.
        @param data: A dictionary containing the jobId, filename and md5Hashsum
        '''
        pass

    def putFinished(self, sender, data):
        '''
        @summary: Global Command. Signals that the previous file transfer
        was completed successfully. Message contains only the global job Id
        @param data: dictionary that contains the jobId
        '''
        pass

    def getResults(self, sender, data):
        '''
        @summary: Global Command. Returns the Results of an Job
        @param data: dictionary that contains the username and jobId
        @result:
        '''
        pass

    def killJob(self, sender, data):
        '''
        @summary: Global Command. Signals the Receiver to kill the job with the
        given jobId.
        @ param data: Dictionary that contains the jobId and an userId
        '''
        pass

    def response(self, sender, data):
        '''
        @summary: A Global response message for the last request.
        @param data: Contains additional data. e.g. a Message or a result of the last request.
        @result:
        '''
        pass


    # Client Commands
    # ===============================================
    def getJobState(self, sender, data):
        '''
        @summary: Client Command. Causes the sender to send the state of a
        given Job to the server.
        @param data: Dictionary that contains the jobId.
        '''
        pass

    def checkForPrograms(self, sender, data):
        '''
        @summary: Client command. Causes the sender to if a list of programs is installed.
        @param sender: the sender of the command.
        @param data: the data dictionary contains a key ("programs")
        which consists of a list of dictionaries. Each dictionary contains a key "programName"
        and a key "programExec". The programName defines the readable Name of the program and
        programExec defines the programs executable to check for.
        @result:
        '''
        pass

    # Server Commands
    # ===============================================
    def workstationInfo(self, sender, data):
        '''
        @summary: Server Command. Updates the workstation informations.
        @param sender: workstation who sends the informations.
        @param data: Dictionary that contains the workstation informations.
        @result:
        '''
        pass

    def jobInfo(self, sender, data):
        '''
        @summary: Server Command. Response to an getState-request.
        @param protocol:
        @param data: A dictionary with all available informations of the job
        @result:
        '''
        pass


    # Server Commands for user Control / Debug purpose
    # ===============================================
    def addJob(self, sender, data):
        '''
        @summary: Server Control Command. Adds a new Job to the scheduler.
        @param sender: The sender who added the job.
        @param data: A dictionary containing the job informations.
        '''
        pass

    def schedule(self, sender, data=None):
        '''
        @summary: Server Command. Forces the PySchedServer to schedule his Queued jobs.
        '''
        pass

    def checkJobs(self, sender, data=None):
        '''
        @summary: Server Command. Forces the PySchedServer to update all jobs in database
        @param protocol:
        @param data: Empty
        @result:
        '''
        pass

    def getJobs(self, sender, data):
        '''
        @summary: Server Command. Returns a list with all active jobs of an user.
        @param protocol:
        @param data: A dictionary containing a user name and a Flag whether to show all
        jobs or only active jobs.
        @result:
        '''
        pass

    def archiveJob(self, sender, data):
        '''
        @summary: Server Command. Marks a job as archived
        @param data: A dictionary containing a job id and user name / id
        @result:
        '''
        pass

    def createUser(self, sender, data):
        '''
        @summary: Server Command. Creates a new user in the database.
        @param sender: the sender who send the request
        @param data: msg contains the user informations. First name, last name, email
        @result:
        '''
        pass

    def getCompiler(self, sender, data):
        '''
        @summary: Server Command. Returns a list of all available compiler.
        @param sender: the sender who send the request
        @param data:
        @result:
        '''
        pass

    def getParser(self, sender, data):
        '''
        @summary: Server Command. Returns a list of all available Parser
        @param sender: the sender who send the request
        @param data:
        @result:
        '''
        pass

    def getWorkstations(self, sender, data):
        '''
        @summary: Server command. Returns a list of all registered workstations.
        @param sender: the sender who send the request
        @param data: Nothing
        @result:
        '''
        pass

    def deleteJob(self, sender, data):
        '''
        @summary: Server Command. Deletes the given job form the server.
        @param sender: the sender who send the request
        @param data: jobId, username
        @result:
        '''
        pass

