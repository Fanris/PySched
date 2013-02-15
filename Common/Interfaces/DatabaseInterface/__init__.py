# -*- coding: utf-8 -*-
'''
Created on 2012-12-04 13:23
@summary:
@author: Martin Predki
'''
from Common.IO.FileUtils import createDirectory

import os

class DatabaseInterface(object):
    '''
    @summary: Abstract class for Database access
    All implementations must inherit this class an override
    the necessary functions.
    '''
    def __init__(self, workingDir):
        '''
        @summary: Basic constructor
        @param workingDir: Path to the workingDir of the scheduler.
        All files create by the Scheduler or should be within this directory
        @result:
        '''
        self.workingDir = createDirectory(os.path.join(workingDir, "database"))

    def addToDatabase(self, obj):
        '''
        @summary: Adds a new object to the database
        @param job: Reference to the PySched-object to add.
        @result: Returns the added object as a PySched Object
        '''
        raise NotImplementedError

    def readFromDatabase(self, type):
        '''
        @summary: Returns a list containing all Elements of the given
        type from the database
        @param type: A PySched-Object type
        @result: Returns a list of all elements of the type within the database
        '''
        raise NotImplementedError

    def updateObject(self, obj):
        '''
        @summary: Updates the given object within the database
        @param job: An PySched-object containing the new values
        @result: Returns the updated object as a PySched object
        '''
        raise NotImplementedError

    def deleteFromDatabase(self, obj):
        '''
        @summary: Deletes an object from the database
        @param obj: PySched-object to delete
        @result:
        '''
        raise NotImplementedError

