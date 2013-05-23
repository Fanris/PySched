# -*- coding: utf-8 -*-
'''
Created on 2012-12-10 15:12
@summary:
@author: Martin Predki
'''


from PySched.Common.Interfaces.WIMInterface import WIMInterface

from twisted.internet.task import LoopingCall

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
    def __init__(self, pySchedClient, interval=5, programs=[]):
        '''
        @summary: Initializes the WIM
        @param interval: time between each information refresh.
        @param programs: A dictionary (programName: programExec) of programs 
        which may be configured on the workstation
        @result:
        '''
        super(WIM, self).__init__(pySchedClient, programs)
        self.logger = logging.getLogger("PySchedClient")
        self.informations = {}
        self.interval = interval
        self.refreshLoop = LoopingCall(self.refreshData)
        self.programList = {}
        for program in programs:
            self.programList[program.programName] = program

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
        return self.informations.copy()
        
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
            "diskAvailable": psutil.disk_usage(
                self.pySchedClient.workingDir)[0] / (1024**3),
            "version": self.pySchedClient.getVersion(),                
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
            "activeJobs": self.pySchedClient.getRunningJobCount(),
            "diskLoad": psutil.disk_usage(self.pySchedClient.workingDir)[3],
            "diskFree": psutil.disk_usage(
                self.pySchedClient.workingDir)[2] / (1024**3),
            "reservedCpus": self.pySchedClient.getReservedCPUCount()
        })

    def checkForPrograms(self, programs):
        '''
        @summary: Updates the list of available programs
        @param programs: a list of dictionaries containing the program name
        and executable to check for.
        @result: a list of
        '''
        for p in programs:
            if p  in self.programList:
                prog = self.programList.get(p.programName, None)
                if prog and prog.equals(p):
                    continue

            else:
                prog = self.programInstalled(p.programExec)
                if prog:
                    self.programList[p] = prog


        self.informations["programs"] = []
        for p in self.programList.keys():
            self.informations["programs"].append(p)        

    def getProgramPath(self, programName):
        '''
        @summary: Returns the full path to the program
        @param programName: The program name
        @result: 
        '''
        return self.programList.get(programName, None)           

    def programInstalled(self, programExec):
        self.logger.debug("Search for executable for {}".format(programExec))

        fpath, fname = os.path.split(programExec)
        if fpath:
            self.logger.debug("Checking {}".format(fpath))
            if self.is_exe(programExec):
                return os.path.join(fpath, fname)
        else:
            self.logger.debug("PATH: {}".format(os.environ["PATH"]))
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, programExec)
                self.logger.debug("Checking {}".format(exe_file))
                if self.is_exe(exe_file):
                    self.logger.debug("File found!")
                    return exe_file


    def is_exe(self, fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
