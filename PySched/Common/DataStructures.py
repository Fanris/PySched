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

    def addLog(self, message):
        self.log.append("[{}]: {}".format(
            datetime.datetime.now(), message))

class Program(object):
    '''
    @summary: Objects of this class represent external programs
    which may be available on the workstations e.g. MatLab, Mathematica.
    The workstation should have a database table with programs which are 
    available in extension to the Workstation Information Manager or
    if the Manager doesn't check for Programs. Entries from the database
    overrides the informations of the WIM if the same program name occurs.
    '''
    def __init__(self):
        self.programName = None

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
        self.userId = None
        self.firstName = None
        self.lastName = None
        self.email = None
        self.admin = False

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
             2: "WAITING_FOR_WORKSTATION",
             3: "COMPILED",
             4: "DISPATCHED",
             5: "RUNNING",
             6: "DONE",
             7: "ABORTED",             
             8: "ERROR",
             9: "COMPILER_ERROR",
             10: "WORKSTATION_ERROR",
             11: "PERMISSION_DENIED",
             12: "SCHEDULER_ERROR",
             90: "ARCHIVED",
             96: "ARCHIVED (DONE)",
             97: "ARCHIVED (ABORTED)",
             98: "ARCHIVED (ERROR)",
             99: "ARCHIVED (COMPILER_ERROR)",
             100: "ARCHIVED (WORKSTATION_ERROR)",
             101: "ARCHIVED (PERMISSION_DENIED)",
             102: "ARCHIVED (SCHEDULER_ERROR)",
             999: "DELETED"}

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
