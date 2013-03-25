'''
Created on 29.08.2012

Contains the Database Tables

@author: Martin Predki
'''


from PySched.Common.DataStructures import Job, User, Compiler, Program
from PySched.Common import str2Datetime, datetime2Str

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import datetime


class Tables(object):
    ''' Class for Table attributes '''

    declBase = declarative_base()

    def __init__(self, engine):
        self.engine = engine

    def createAllTables(self):
        Tables.declBase.metadata.create_all(self.engine)

class SqliteCompiler(Tables.declBase):
    '''
    @summary: Server side Compiler Table.
    '''
    __tablename__ = "compiler"
    id = Column("id", Integer, primary_key=True)
    compilerName = Column('compilerName', String)
    compilerDescription = Column('compilerDescription', String)

    def __init__(self, compilerName, compilerDescription):
        self.compilerName = compilerName
        self.compilerDescription = compilerDescription

    def update(self, updatedObject):
        '''
        @summary: Updates this object with the new values
        @param updatedObject:
        @result:
        '''
        self.compilerName = updatedObject.compilerName
        self.compilerDescription = updatedObject.compilerDescription

    def convertToPySched(self):
        '''
        @summary: Converts this Sqlite object object to a PySched object
        @result: A PySched object
        '''
        compiler = Compiler()
        compiler.id = self.id
        compiler.compilerDescription = self.compilerDescription

        return compiler

    @staticmethod
    def convertFromPySched(obj):
        '''
        @summary: Converts the PySchedServer object to an Sqlite object
        @param obj: Object to convert
        @result:
        '''
        compiler = SqliteCompiler(obj.compilerName, obj.compilerDescription)
        compiler.id = obj.compilerId

        return compiler

class SqliteProgram(Tables.declBase):
    '''
    @summary: Server side Compiler Table.
    '''
    __tablename__ = "programs"
    id = Column("id", Integer, primary_key=True)
    programName = Column('programName', String)
    programVersion = Column('programVersion', String)
    programExec = Column('programExec', String)

    def __init__(self, programName, programExec, programVersion):
        self.programName = programName
        self.programExec = programExec
        self.programVersion = programVersion

    def update(self, updatedObject):
        '''
        @summary: Updates this object with the new values
        @param updatedObject:
        @result:
        '''
        self.programName = updatedObject.programName
        self.programExec = updatedObject.programExec
        self.programVersion = updatedObject.programVersion

    def convertToPySched(self):
        '''
        @summary: Converts this Sqlite object object to a PySched object
        @result: A PySched object
        '''
        program = Program()
        program.id = self.id
        program.programName = self.programName
        program.programExec = self.programExec
        program.programVersion = self.programVersion

        return program

    @staticmethod
    def convertFromPySched(obj):
        '''
        @summary: Converts the PySchedServer object to an Sqlite object
        @param obj: Object to convert
        @result:
        '''
        program = SqliteProgram(obj.programName, obj.programExec, obj.programVersion)
        program.id = obj.id

        return program


class SqliteUser(Tables.declBase):
    '''
    @summary: Server side User table
    '''
    __tablename__ = "users"
    id = Column('id', Integer, primary_key=True)
    firstName = Column('firstName', String)
    lastName = Column('lastName', String)
    email = Column('email', String)
    admin = Column('admin', Boolean)


    def __init__(self, email):
        self.email = email
        self.admin = False

    def __repr__(self):
        print "User ({}, {})".format(self.id, self.email)

    def update(self, updatedObject):
        '''
        @summary: Updates this object with the new values
        @param updatedObject:
        @result:
        '''
        self.firstName = updatedObject.firstName
        self.lastName = updatedObject.lastName
        self.email = updatedObject.email
        self.admin = updatedObject.admin

    def convertToPySched(self):
        '''
        @summary: Converts this SqliteUser object to a PySched user object
        @result: A PySched user object
        '''
        user = User()
        user.id = self.id
        user.firstName = self.firstName
        user.lastName = self.lastName
        user.email = self.email
        user.userId = self.email
        user.admin = self.admin

        return user

    @staticmethod
    def convertFromPySched(obj):
        '''
        @summary: Converts the PySchedServer object to an SqliteUser object
        @param user:
        @result:
        '''
        newUser = SqliteUser(obj.userId)
        newUser.id = obj.id
        newUser.firstName = obj.firstName
        newUser.lastName = obj.lastName
        newUser.admin = obj.admin

        return newUser


class SqliteJob(Tables.declBase):
    ''' Server side Job table '''

    __tablename__ = "jobs"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    jobDescription = Column("jobDescription", String)
    userId = Column('userId', Integer, ForeignKey(SqliteUser.id))
    multiCpu = Column('multiCpu', Boolean)
    minCpu = Column('minCpu', Integer)
    minMemory = Column('minMemory', Integer)
    reqOS = Column('reqOS', String)
    reqPrograms = Column('requiredPrograms', String)
    compilerStr = Column('compilerStr', String)
    executeStr = Column('executeStr', String)
    added = Column('added', DateTime)
    started = Column('started', DateTime)
    finished = Column('finished', DateTime)
    stateId = Column('stateId', Integer)
    workstation = Column('workstation', String)

    user = relationship("SqliteUser", backref=backref('jobs', order_by=id))

    def __init__(self):
        '''
        @summary: Creates an Job instance.
        @result: a new Job instance
        '''
        self.name = None
        self.jobDescription = None
        self.userId = None
        self.multiCpu = False
        self.minCpu = 1
        self.minMemory = None
        self.reqOS = None
        self.reqPrograms = None
        self.compilerStr = None
        self.executeStr = None
        self.added = datetime.datetime.now()
        self.started = None
        self.finished = None
        self.stateId = 0
        self.workstation = None

    def update(self, updatedObject):
        '''
        @summary: Updates this object with the new values
        @param updatedObject:
        @result:
        '''
        self.name = updatedObject.name
        self.jobDescription = updatedObject.jobDescription
        self.userId = updatedObject.userId
        self.multiCpu = updatedObject.multiCpu
        self.minCpu = updatedObject.minCpu
        self.minMemory = updatedObject.minMemory
        self.reqOS = updatedObject.reqOS
        self.reqPrograms = updatedObject.reqPrograms
        self.compilerStr = updatedObject.compilerStr
        self.executeStr = updatedObject.executeStr
        self.added = updatedObject.added
        self.started = updatedObject.started
        self.finished = updatedObject.finished
        self.stateId = updatedObject.stateId
        self.workstation = updatedObject.workstation


    def convertToPySched(self):
        '''
        @summary: Converts this Sqlite object object to a PySched object
        @result: A PySched object
        '''
        job = Job()
        job.jobId = self.id
        job.jobName = self.name
        job.jobDescription = self.jobDescription
        job.reqOS = self.reqOS
        job.reqPrograms = self.reqPrograms.split(';')
        job.compilerStr = self.compilerStr
        job.executeStr = self.executeStr
        job.userId = self.userId
        job.multiCpu = self.multiCpu
        job.minCpu = self.minCpu
        job.minMemory = self.minMemory
        job.added = datetime2Str(self.added)
        job.started = datetime2Str(self.started)
        job.finished = datetime2Str(self.finished)
        job.stateId = self.stateId
        job.workstation = self.workstation

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

        job = SqliteJob()
        job.id = obj.jobId
        job.name = obj.jobName
        job.jobDescription = obj.jobDescription
        job.userId = obj.userId
        job.multiCpu = obj.multiCpu
        job.minCpu = obj.minCpu
        job.minMemory = obj.minMemory
        job.reqOS = obj.reqOS
        job.reqPrograms = reqPrograms
        job.compilerStr = obj.compilerStr
        job.executeStr = obj.executeStr
        job.added = str2Datetime(obj.added)
        job.started = str2Datetime(obj.started)
        job.finished = str2Datetime(obj.finished)
        job.stateId = obj.stateId
        job.workstation = obj.workstation

        return job
