# -*- coding: utf-8 -*-
'''
Created on 2012-12-10 15:12
@summary:
@author: Martin Predki
'''

from twisted.internet.task import LoopingCall

from Common.Interfaces.WIMInterface import WIMInterface

import psutil
import platform
import os
import logging

class WIM(WIMInterface):
    '''
    @summary: The WIM (Workstation Information Manager) is used to gather all relevant
    informations of the workstation (eg. cpu load, used memory, etc.) and store them.
    This class uses psutil (http://code.google.com/p/psutil/) to get the informations.
    '''
    def __init__(self, interval=5, programs=[]):
        '''
        @summary: Initializes the WIM
        @param interval: time between each information refresh.
        @param programs: A dictionary (programName: programExec) of programs 
        which may be configured on the workstation
        @result:
        '''
        super(WIM, self).__init__(programs)
        self.logger = logging.getLogger("PySchedClient")
        self.informations = {}
        self.interval = interval
        self.refreshLoop = LoopingCall(self.refreshData)

    def startCollectingData(self):
        '''
        @summary: Starts the refresh loop
        @result:
        '''
        self.informations = {}
        self.getStaticInformations()
        self.refreshLoop.start(self.interval, now=True)

    def stopCollectingData(self):
        '''
        @summary: Stops the refresh loop
        @result:
        '''
        self.refreshLoop.stop()


    def getWorkstationInformations(self):
        '''
        @summary: Returns a dictionary with all workstation informations.
        @result:
        '''
        info = self.informations.copy()
        progs = info.get("programs", None)
        if progs:
            info["programs"] = progs.keys()

        return info

    def getStaticInformations(self):
        '''
        @summary: Sets the static informations of the system like os, name, machine
        @result: returns a dictionary containing all static machine informations
        '''
        self.informations.update({
            "os": platform.system(),
            "workstationName": platform.node(),
            "machine": platform.machine(),
            "cpuCount": psutil.NUM_CPUS,
            "memory": psutil.virtual_memory()[0] / (1024**3),
        })

    def refreshData(self):
        '''
        @summary: Refreshes all workstation informations. This function is called by the
        refresh loop.
        @result: Returns a dictionary with all dynamic workstations informations
        '''
        self.informations.update({
            "cpuLoad": psutil.cpu_percent(interval=0, percpu=True),
            "memoryLoad": psutil.virtual_memory()[2],
            "activeUsers": len(psutil.get_users()),
        })

    def checkForPrograms(self, programs):
        '''
        @summary: Updates the list of available programs
        @param programs: a list of dictionaries containing the program name
        and executable to check for.
        @result: a list of
        '''
        self.informations["programs"] = self.getProgramList(programs)

    def getProgramPath(self, programName):
        '''
        @summary: Returns the full path to the program
        @param programName: The program name
        @result: 
        '''
        if self.informations.get("programs", None):
            return self.informations["programs"].get(programName, None)
            

    def getProgramList(self, programs):
        '''
        @summary: Checks if a given list of programs are available via the environment
        @param program: a list of dictionaries containing the program name
        and executable to check for.
        @result: Returns a list with all available programs
        '''
        progs = {}
        for program in programs:
            programName = program.get("programName", None)
            programExec = program.get("programExec", None)
            if not programName or not programExec:
                continue

            programPath = self.programInstalled(programName, programExec)
            if programPath:                
                progs[programName] = programPath
                self.logger.debug("Program available: {}".format(program))
            else:
                self.logger.debug("Program not available: {}".format(program))
                
        return progs

    def programInstalled(self, programName, programExec):

        if programName in self.programList:
            return self.programList.get(programName, None)

        fpath, fname = os.path.split(programExec)
        if fpath:
            if self.is_exe(programExec):
                return os.path.join(fpath, fname)
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, programExec)
                if self.is_exe(exe_file):
                    return exe_file


    def is_exe(self, fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
