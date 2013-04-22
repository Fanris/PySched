# -*- coding: utf-8 -*-
'''
Created on 2013-01-14 15:33
@summary:
@author: Martin Predki
'''

class WIMInterface(object):
    '''
    @summary: This Interface defines all functions that must be implemented
    by an Workstation Information Manager (WIM). It is highly recommended that
    the WorkstationReference.py is updated according to the provided workstation informations.
    '''
    def __init__(self, pySchedClient, programs=[]):
        '''
        @summary: The consturctor takes one parameter containing 
        @param programs: a dictionary
        with all preconfigured programs on the workstation which may be defined
        by database entries. This dictionary is stored in programList
        @result: 
        '''
        self.pySchedClient = pySchedClient
        self.programList = {}
        if not programs:
            return
            
        for p in programs:
            self.programList[p.programName] = p.programExec

    def getWorkstationInformations(self):
        '''
        @summary: This function is called by the PySchedClient and should get the current
        workstation informations.
        @result: a dictionary containing the workstation information. See WorkstationReference.py
        for further informations on the dictionary.
        '''
        raise NotImplementedError

    def checkForPrograms(self, program):
        '''
        @summary: This function is called by the PySchedClient when the WIM should check
        if a given list of programs is available at the workstation. Every available program
        should be added to the workstation information dictionary (see workstationReference.py)
        @param program: a list of dictionaries of programs to check for. Each dictionary consists
        of a key "programName" which describes the readable name of the program and a key "exe"
        which describes the name of the executable to check for. Within the workstation information
        dictionary only the program name is needed (and expected)
        @result:
        '''
        raise NotImplementedError

    def getProgramPath(self, programName):
        '''
        @summary: This function is called by the PySchedClient when the full 
        path to an installed program is needed. The function should return None
        if the program is not installed or not checked.
        @param programName: The name of the program to search for.
        @result: 
        '''
        raise NotImplementedError

