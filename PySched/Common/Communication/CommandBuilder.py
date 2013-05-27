'''
Created on 17.08.2012

Common functions and parameter for PySched-Networking

@author: Martin Predki
'''
import json

class CommandBuilder(object):
    '''
    Class to build command strings. A command string consists of an command and a list
    of key-value-pairs. It is send and parsed as a JSON object except the EndOfFile command.
    The EndOfFile command is used to signal the end of an file transfer.
    Server Commands are received and parsed by the PySchedServer.
    Client Commands are received and parsed by the PySchedClient.
    '''
    @staticmethod
    def buildCommand(command, endCom=False, **kwargs):
        '''
        @summary: Generates a generic network command.
        @param command: The network command
        @param **kwargs: a list of keywords which are send as parameter.
        @result:
        '''
        msg = {"command": command}
        for key, value in kwargs.iteritems():
            msg[key] = value

        if endCom:
            msg["endCom"] = True

        return json.dumps(msg)

    @staticmethod
    def EndOfFile():
        '''
        @summary: Returns the EndOfFile String
        @param :
        @result:
        '''
        return "/EOF"

    @staticmethod
    def buildResponseString(result, **additionalInfos):
        '''
        @summary: Is used as a Response for all request. A response String always ends the communication.
        @param result: The result of the request. It may be True or False
        @param **additionalInfos: A dictionary containing Additional informations.
        E.g. an error message
        @result:
        '''
        return CommandBuilder.buildCommand("response", endCom=True, result=result, **additionalInfos)

    @staticmethod
    def buildMessageString(message, endCom=False):
        '''
        @summary: Global Command. Creates a Message.
        @param message: Message to send.
        '''
        if not endCom:
            return CommandBuilder.buildCommand("msg", endCom=endCom, message=message)

    @staticmethod
    def buildPutString(jobId, filename, hashsum):
        '''
        @summary: Global Command. Creates a put command.
        @param jobId: ID of the job to which this file belongs
        @param filename: The filename
        @param hashsum: MD5-Hashsum of the file
        '''
        return CommandBuilder.buildCommand("put", jobId=jobId, filename=filename, md5=hashsum)

    @staticmethod
    def buildAddJobString(**jobInformations):
        '''
        @summary: Global Command. Creates an addJob command.
        @param **jobInformations: the job informations
        @result:
        '''
        return CommandBuilder.buildCommand("addJob", **jobInformations)


    @staticmethod
    def buildPingString():
        '''
        @summary: Server UDP Command. Creates a Ping command.
        '''
        return CommandBuilder.buildCommand("ping")

    @staticmethod
    def buildServerAvailableString():
        '''
        @summary: Server UDP Command. Creates a Server available message.
        '''
        return CommandBuilder.buildCommand("serverAvailable", endCom=True)

    @staticmethod
    def buildWorkstationInfoString(**workstationInfo):
        '''
        @summary: Server Command. Creates a /workstationInfo command.
        @param **workstationInfo: A List of key-value-pairs which
        contains the workstation informations.
        @result:
        '''
        return CommandBuilder.buildCommand("workstationInfo", **workstationInfo)

    @staticmethod
    def buildJobInformationString(**jobInformations):
        '''
        @summary: Server Command. Creates a /jobInfo Command.
        @param **jobInformations: A List of key-value-pairs which
        contains the job informations.
        @result:
        '''
        return CommandBuilder.buildCommand("jobInfo", **jobInformations)

    @staticmethod
    def buildPutFinishedString(jobId, filename):
        '''
        @summary: Server Command. Creates a put finished command to signal the server
        that the put command for the given job id was successful and file was transfered.
        This command is only send by a workstation.
        @param jobId: The id of the transfered job.
        @result:
        '''
        return CommandBuilder.buildCommand("putFinished", jobId=jobId, filename=filename)


    @staticmethod
    def buildGetResultsString(jobId):
        '''
        @summary: Client Command. Creates a get results command.
        @param jobId: ID of the job.
        @result:
        '''
        return CommandBuilder.buildCommand("getResults", jobId=jobId)

    @staticmethod
    def buildGetJobStateString(jobId):
        '''
        @summary: Client Command. Creates a get Status command.
        The get status command (/getStatus <jobId>) is used to retrieve
        the state of the given job.
        @param jobId:
        @result:
        '''
        return CommandBuilder.buildCommand("getJobState", jobId=jobId)

    @staticmethod
    def buildKillJobString(jobId):
        '''
        @summary: Client Command. Creates a kill job command.
        The kill job command (/killJob <jobId>) is used to terminate a
        running Job on client side.
        @param jobId:
        @result:
        '''
        return CommandBuilder.buildCommand("killJob", jobId=jobId)

    @staticmethod
    def buildCheckForProgramsString(programs):
        '''
        @summary: Client command. Creates a checkForPrograms command.
        This command is used to check if the given programs are available at
        the workstation. They are listed in the next workstation information dict.
        @param programs: A list of program names
        @result:
        '''
        return CommandBuilder.buildCommand("checkForPrograms", programs=programs)

    @staticmethod
    def buildReserveCPUString(jobId):
        '''
        @summary: Client command. Reserves a CPU on the client for 30 min.
        @param jobId: the jobId of the job for which the cpu is reserved.
        @result: 
        '''
        return CommandBuilder.buildCommand("reserveCPU", jobId=jobId)

    @staticmethod
    def buildUpdatePathString(path):
        '''
        @summary: Client command. Updates the Path list on the client.
        @param path: the path to append
        @result: 
        '''
        return CommandBuilder.buildCommand("updatePath", path=path)

    @staticmethod
    def buildShutdownString():
        return CommandBuilder.buildCommand("shutdown")

    @staticmethod
    def buildPauseJobString(jobId):
        return CommandBuilder.buildCommand("pauseJob", jobId=jobId)

    @staticmethod
    def buildResumeJobString(jobId):
        return CommandBuilder.buildCommand("resumeJob", jobId=jobId)
