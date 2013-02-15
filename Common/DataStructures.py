# -*- coding: utf-8 -*-
'''
Created on 2012-12-04 13:34
@summary: This package contains all data structures used by PySched.
@author: Martin Predki
'''

import datetime

class Job(object):
    '''
    @summary: Objects of this class represent a scheduler job
    '''

    def __init__(self):
        '''
        @summary: Initializes a job object
        @result:
        '''
        # global informations
        self.jobId = None
        self.jobName = None
        self.jobDescription = None
        self.userId = None

        # Pre-process informations
        self.compilerStr = None

        # Scheduling informations
        self.multiCpu = False
        self.minCpu = 1
        self.minMemory = None
        self.reqOS = None
        self.reqPrograms = []

        # Process informations:
        self.executeStr = None

        # Job informations
        self.added = None
        self.started = None
        self.finished = None
        self.stateId = 0
        self.workstation = None

        self.log = []

        self.otherAttr = {}

    def createLogHead(self):
        '''
        @summary: Creates the Log head for this job
        @result: a list containing the lines of the log head.
        '''
        head = []
        head.append("+---------------------------------------------+")
        head.append("|               PySched Job log               |")
        head.append("+---------------------------------------------+")
        head.append("")
        head.append("Global information:")
        head.append("-------------------")
        head.append("jobId: {}".format(self.jobId))
        head.append("jobName: {}".format(self.name))
        head.append("jobDescription: {}".format(self.jobDescription))
        head.append("jobState: {}".foramt(self.stateId))
        head.append("userId: {}".format(self.userId))
        head.append("")

        head.append("Job information:")
        head.append("-------------------")
        head.append("Support multiple cpus: {}".format(self.multiCpu))
        head.append("Minimum cpu count: {}".format(self.minCpu))
        head.append("Minimum memory: {}".format(self.minMemory))
        head.append("Needed programs: {}".format(self.reqPrograms))
        head.append("added: {}".format(self.added))
        head.append("started: {}".format(self.started))
        head.append("finished: {}".format(self.finished))
        head.append("workstation: {}".format(self.workstation))
        head.append("")

        head.append("Compiler information:")
        head.append("-------------------")
        head.append("CompilerStr: {}".format(self.compilerStr))
        head.append("")

        head.append("Other Attributes:")
        head.append("-----------------")

        for key in self.otherAttr.keys:
            head.append(key + ": {}".format(self.otherAttr[key]))

        head.append("")
        head.append("")

        return head

    def addToLog(self, logType, message):
        '''
        @summary: Adds a message to the log.
        @param logType: Type of the Message. E.g. "Log", "Error"
        @param message: The message
        @result:
        '''
        log = "[" + str(datetime.datetime.now()).split(".")[0] + "]"
        log += " [{}]: ".format(logType.uppercase())
        log += message

        self.log.append(log)

    def getLog(self):
        '''
        @summary: Returns a list of lines containing the complete job Log
        @result:
        '''
        completeLog = []
        completeLog.extend(self.createLogHead())
        completeLog.extend(self.log)

        return completeLog

class Program(object):
    '''
    @summary: Objects of this class represent external programs
    which may be available on the workstations e.g. MatLab, Mathematica
    '''
    def __init__(self):
        self.programName = None
        self.programExec = None


class User(object):
    '''
    @summary: Objects of this class represent an user
    '''
    def __init__(self):
        '''
        @summary: Initializes a user object
        @result:
        '''
        self.id = None
        self.username = None
        self.firstName = None
        self.lastName = None
        self.email = None

        self.otherAttr = {}

class Compiler(object):
    '''
    @summary: Objects of this class represent a compiler
    '''
    def __init__(self):
        '''
        @summary: Initializes a compiler object
        @result:
        '''
        self.id = None
        self.compilerName = None
        self.compilerDescription = None

        self.otherAttr = {}


class JobState(object):
    '''
    @summary: Lookup dictionary for job states
    '''
    table = {0: "QUEUED",
             1: "PREPARED",
             2: "COMPILED",
             3: "DISPATCHED",
             4: "RUNNING",
             5: "DONE",
             6: "ABORTED",
             7: "SCHEDULER_ERROR",
             8: "COMPILER_ERROR",
             9: "WORKSTATION_ERROR",
             10: "PERMISSION_DENIED",
             11: "ERROR",
             99: "ARCHIVED",
             100: "DELETED"}

    @staticmethod
    def lookup(state):
        '''
        @summary: Returns the state to the stateId
        @param sateId:
        @result:
        '''
        if JobState.table.has_key(state):
            return JobState.table[state]
        else:
            for key in JobState.table.keys():
                if state == JobState.table[key]:
                    return key

        return None
