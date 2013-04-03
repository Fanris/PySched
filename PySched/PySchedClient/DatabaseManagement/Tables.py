'''
Created on 29.08.2012

Contains the Database Tables

@author: Martin Predki
'''


from PySched.Common.DataStructures import Job, Program
from PySched.Common import str2Datetime, datetime2Str

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

import datetime


class Tables(object):
    ''' Class for Table attributes '''

    declBase = declarative_base()

    def __init__(self, engine):
        self.engine = engine

    def createAllTables(self):
        Tables.declBase.metadata.create_all(self.engine)

class SqliteJob(Tables.declBase):
    ''' Client side Job table '''

    __tablename__ = "jobs"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    jobDescription = Column("jobDescription", String)
    reqPrograms = Column("requiredPrograms", String)
    executeStr = Column('executeStr', String)
    added = Column('added', DateTime)
    started = Column('started', DateTime)
    finished = Column('finished', DateTime)
    stateId = Column('stateId', Integer)
    log = Column('log', String)

    def __init__(self, name, jobDescription, executeStr):
        '''
        @summary: Creates an Job instance.
        @param name: Name of the Job
        @param solverId: Id of the Solver to use.
        @param userId: Id of the user
        @param parameter: Job parameter list
        @result: a new Job instance
        '''
        self.name = name
        self.jobDescription = jobDescription
        self.executeStr = executeStr
        self.reqPrograms = []
        self.added = datetime.datetime.now()
        self.started = None
        self.finished = None
        self.stateId = 0
        self.log = None

    def update(self, updatedObject):
        '''
        @summary: Updates this object with the new values
        @param updatedObject:
        @result:
        '''
        self.name = updatedObject.name
        self.jobDescription = updatedObject.jobDescription
        self.executeStr = updatedObject.executeStr
        self.reqPrograms = updatedObject.reqPrograms
        self.added = updatedObject.added
        self.started = updatedObject.started
        self.finished = updatedObject.finished
        self.stateId = updatedObject.stateId
        self.log = updatedObject.log

    def convertToPySched(self):
        '''
        @summary: Converts this Sqlite object object to a PySched object
        @result: A PySched object
        '''
        job = Job()
        job.jobId = self.id
        job.jobName = self.name
        job.jobDescription = self.jobDescription
        job.executeStr = self.executeStr
        job.reqPrograms = self.reqPrograms.split(';')
        job.added = datetime2Str(self.added)
        job.started = datetime2Str(self.started)
        job.finished = datetime2Str(self.finished)
        job.stateId = self.stateId
        job.log = self.log.split(';')

        return job

    @staticmethod
    def convertFromPySched(obj):
        '''
        @summary: Converts the PySchedServer object to an Sqlite object
        @param obj: Object to convert
        @result:
        '''
        reqPrograms = ""
        for progs in obj.reqPrograms:
            reqPrograms += progs + ";"
        reqPrograms = reqPrograms.rstrip(";")

        log = ""
        for l in obj.log:
            log += l + ";"
        log = log.rstrip(";")        

        job = SqliteJob(obj.jobName, obj.jobDescription, obj.executeStr)
        job.id = obj.jobId
        job.reqPrograms = reqPrograms
        job.added = str2Datetime(obj.added)
        job.started = str2Datetime(obj.started)
        job.finished = str2Datetime(obj.finished)
        job.stateId = obj.stateId
        job.log = log

        return job  

class SqliteProgram(Tables.declBase):
    ''' Client side Program table '''

    __tablename__ = "programs"
    id = Column("id", Integer, primary_key=True)
    name = Column("programName", String)
    path = Column("programExec", String)

    def __init__(self, programName, programExec):
        self.name = programName
        self.path = programExec

    def update(self, updatedObject):
        '''
        @summary: Updates this object with the new values
        @param updatedObject:
        @result:
        '''
        self.name = updatedObject.name
        self.path = updatedObject.path

    def convertToPySched(self):
        '''
        @summary: Converts this Sqlite object object to a PySched object
        @result: A PySched object
        '''
        program = Program()
        program.programName = self.name
        program.programExec = self.path

        return program

    @staticmethod
    def convertFromPySched(obj):
        '''
        @summary: Converts the PySchedServer object to an Sqlite object
        @param obj: Object to convert
        @result:
        '''
        program = SqliteProgram(obj.programName, obj.programExec)

        return program
