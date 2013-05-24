# -*- coding: utf-8 -*-
'''
Created on 08.08.2012

 PySched-Client. Waits for a PySched-Server to connect to. PySched-Client
 is capable of sending it's host computer CPU-usage data to the PySched-Server
 and running various programs given by the PySched-Server

@author: Martin Predki
'''

from PySched.Common.Communication.CommandBuilder import CommandBuilder
from PySched.Common.IO import FileUtils, Archive
from PySched.Common import datetime2Str
from PySched.Common.DataStructures import Job, JobState, Program

from DatabaseManagement import SqliteManager
from WorkstationInformationManager import WIM
from JobRunner import JobRunner
from NetworkManagement import NetworkManager
from MessageHandler import MessageHandler

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import os
import logging
import datetime

VERSION = "1.2.2"
TITLE = """
 _____        _____      _              _  _____ _ _            _    
|  __ \      / ____|    | |            | |/ ____| (_)          | |   
| |__) |   _| (___   ___| |__   ___  __| | |    | |_  ___ _ __ | |_  
|  ___/ | | |\___ \ / __| '_ \ / _ \/ _` | |    | | |/ _ \ '_ \| __| 
| |   | |_| |____) | (__| | | |  __/ (_| | |____| | |  __/ | | | |_  
|_|    \__, |_____/ \___|_| |_|\___|\__,_|\_____|_|_|\___|_| |_|\__| 
        __/ |                        Copyright 2012 by Martin Predki 
       |___/                         Version {}                     

====================================================================
""".format(VERSION)


class PySchedClient(object):
    def __init__(self, workingDir, args):
        '''
        @summary: Initializes the PySchedClient.
        @param workingDir: The directory in which the PyschedClient works.
        The user running the PySchedClient needs read/write-rights on this folder.
        @param args: passed arguments from the start script
        @result:
        '''
        self.workingDir = os.path.normpath(workingDir)
        FileUtils.createDirectory(workingDir)

        self.initializeLogger(self.workingDir, args)
        self.debugMode = args.debug

        if not args.quiet:
            self.printTitle()

        self.logger.info("Starting PySchedClient v{}".format(VERSION))

        # Init
        self.reservedCpus = {}

        # Load additional Path
        if os.path.exists(os.path.join(self.workingDir, "PATHS")):
            self.logger.info("Reading additional PATHS...")
            paths = FileUtils.readFile(os.path.join(self.workingDir, "PATHS"))
            for p in paths:
                self.updatePathEnv(p)


        # Job Runner
        self.jobRunner = JobRunner(self)

        # Database. Database class needs to extend Common.Interfaces.DatabaseInterface
        self.dbController = SqliteManager(self.workingDir)
        self.logger.info("Database Manager initialized.")

        # WIM
        self.wim = WIM(self)
        self.wim.startCollectingData()
        self.workstationStateLoop = LoopingCall(self.sendWorkstationState)
        self.logger.info("Workstation Information Manager initialized.")

        # Network. NetworkManager needs to extend Common.Interfaces.Network.NetworkInterface
        self.logger.info("Starting network server...")
        rsaKey = args.key or os.path.join(self.workingDir, 'pysched.rsa')
        self.networkManager = NetworkManager(
            self.workingDir, 
            MessageHandler(self), 
            rsaKey,
            multiGroup=args.multicast)
        self.networkManager.startService()
        self.serverId = None        

        self.checkJobs()
        reactor.run()

    # Initialize Functions
    # =====================================================
    def startWorkstationStateLoop(self):
        '''
        @summary: Starts the workstation state loop
        @result:
        '''
        self.logger.info("Starting the workstation information loop...")
        self.workstationStateLoop.start(10, now=True)

    def stopWorkstationStateLoop(self):
        '''
        @summary: Stops the workstation state loop
        @result:
        '''
        self.logger.info("Stopping the workstation information loop...")
        self.workstationStateLoop.stop()

    def sendWorkstationState(self):
        '''
        @summary: Sends the workstation state to the server.
        @result:
        '''
        self.logger.debug("Sending workstation state to server...")
        self.networkManager.sendMessage(self.serverId, 
            CommandBuilder.buildWorkstationInfoString(
                **self.wim.getWorkstationInformations()))

    def startNetworkServices(self):
        '''
        @summary: Starts the network services
        @result:
        '''
        self.networkManager.startService()

    def stopNetworkServices(self):
        '''
        @summary: Stops the network services
        @result:
        '''
        self.networkManager.stopService()

    def connectionMade(self):
        '''
        @summary: Is called when the network manager is connected.
        @result:
        '''
        self.startWorkstationStateLoop()

    # Database Functions
    # =====================================================
    def addToDatabase(self, obj):
        '''
        @summary: Adds the given object to the database
        @param obj: The object to add.
        @result:
        '''
        return self.dbController.addToDatabase(obj)


    def getFromDatabase(self, objClass, first=False, **filterArgs):
        '''
        @summary: Returns a list of all <type> that passes the filter
        from the database.
        @param type: Which object should be read from the database
        @param **filterArgs: a List of filters to use. E.g. id=0
        @result:
        '''
        objects = self.dbController.getFromDatabase(objClass)
        self.logger.debug("Retrieved {} object from database".format(len(objects)))

        returnList = filter(self.createFilterFunction(**filterArgs), objects)
        self.logger.debug("{} of {} objects passed the filter function ({})".format(len(returnList), len(objects), filterArgs))

        if len(returnList) == 0:
            return None

        if first:
            return returnList[0]

        return returnList

    def updateDatabaseEntry(self, obj):
        '''
        @summary: Updates the entry within the database
        @param obj: the object to update
        @result:
        '''
        return self.dbController.updateDatabaseEntry(obj)


    def createFilterFunction(self, **filterArgs):
        '''
        @summary: Creates a function from filterArgs to be used in
        a filter.
        @param **filterArgs:
        @result:
        '''
        def checkItem(item):
            for key, value in filterArgs.iteritems():
                self.logger.debug("Check object for {}={}".format(key, value))
                if str(getattr(item, key, None)) != str(value):
                    self.logger.debug("Object discarded. Key: {}, Value: {}, Needed Value: {}".format(key, getattr(item, key, None), value))
                    return False
                self.logger.debug("Object passed.")

            return True
        return checkItem

    # PySchedFunctions
    # =====================================================
    def getProgramPath(self, programName):
        '''
        @summary: Returns the full path of an installed programs (if in the list)
        @param programName: The program name
        @result: 
        '''
        return self.wim.getProgramPath(programName)

    def getProgramsFromDatabase(self):
        '''
        @summary: Returns a list with all programs specified in the database
        @result: 
        '''
        return self.getFromDatabase(Program)

    def reserveCPU(self, jobId):
        '''
        @summary: Reserves a CPU for an job.
        @param jobId: the jobId
        @result: 
        '''
        if jobId:
            self.reservedCpus[jobId] = reactor.callLater(
                1800, self.setCpuFree, jobId)

    def setCpuFree(self, jobId):
        '''
        @summary: Deletes a job reservation.
        @param jobId:
        @result: 
        '''
        try:
            del self.reservedCpus[jobId]
        except:
            pass

    def getReservedCPUCount(self):
        '''
        @summary: Returns the count of reserved CPUS
        @result: 
        '''
        return len(self.reservedCpus)


    # Job Control Functions
    # =====================================================
    def addJob(self, jobInformations):
        '''
        @summary: Adds a new job to the database.
        @param jobInformations: A dictionary containing the job informations
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobInformations["jobId"], first=True)

        if not job:
            job = Job()
            job.__dict__.update(jobInformations)
            self.addToDatabase(job)
        else:
            job.__dict__.update(jobInformations)
            self.updateDatabaseEntry(job)

    def runJob(self, jobId):
        '''
        @summary: Runs the job with the given id.
        @param jobId: the id of the job to run
        @result:
        '''
        self.logger.info("Starting job {}...".format(jobId))
        job = self.getFromDatabase(Job, jobId=jobId, first=True)

        if not job:
            self.logger.error("No Job with id {} found.".format(jobId))

        self.createFileIndex(jobId)

        if not self.jobRunner.runJob(job):
            job.stateId = JobState.lookup("WORKSTATION_ERROR")
            job.started = datetime2Str(datetime.datetime.now())
            job.finished = job.started
            self.updateDatabaseEntry(job)
            self.setCpuFree(jobId)
            self.logger.info("Sending updated JobState of Job {}".format(job.jobId))
            self.networkManager.sendMessage(self.serverId, CommandBuilder.buildJobInformationString(**job.__dict__))

    def jobStarted(self, jobId):
        '''
        @summary: Is called when a job is started.
        @param jobId: the started job
        @result: 
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        job.stateId = JobState.lookup("RUNNING")
        job.started = datetime2Str(datetime.datetime.now())        
        self.updateDatabaseEntry(job)
        self.logger.info("Sending updated JobState of Job {}".format(job.jobId))
        self.networkManager.sendMessage(self.serverId, CommandBuilder.buildJobInformationString(**job.__dict__))
        self.sendWorkstationState()

    def jobEnded(self, jobId, done=False, aborted=False, error=False):
        '''
        @summary: Is called when the job is Done
        @param job:
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        job.finished = datetime2Str(datetime.datetime.now())

        if  job.stateId == JobState.lookup("RUNNING"):
            if done:
                job.stateId = JobState.lookup("DONE")
            elif aborted:
                job.stateId = JobState.lookup("ABORTED")
            elif error:
                job.stateId = JobState.lookup("ERROR")

        self.updateDatabaseEntry(job)
        self.cleanupJobDir(jobId)
        self.networkManager.sendMessage(self.serverId, 
            CommandBuilder.buildJobInformationString(**job.__dict__))

    def getRunningJobCount(self):
        '''
        @summary: Returns the count of currently running Jobs.
        @result: 
        '''
        return self.jobRunner.getRunningJobCount()


    # Command Handler
    # =====================================================
    def abortJob(self, jobId):
        '''
        @summary: sends a kill signal to the given job
        @param jobId: The id of the job to kill.
        @result:
        '''
        self.logger.info("Stopping job {}".format(jobId))
        self.jobRunner.abortJob(jobId)

    def returnJobState(self, jobId):
        '''
        @summary: Returns the jobState of the requested job to the server.
        @param jobId: the job Id
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        if job:
            self.logger.info("Sending informations on job {}".format(job.jobId))
            self.networkManager.sendMessage(self.serverId, CommandBuilder.buildJobInformationString(**job.__dict__))

    def returnResults(self, jobId):
        '''
        @summary: Returns the results of the given job
        @param jobId:
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        if job and job.stateId >= JobState.lookup("DONE"):
            jobDir = os.path.join(self.workingDir, str(job.jobId))
            if not os.path.exists(jobDir):
                return False

            archivePath = os.path.join(self.workingDir, "temp", "{}.tar".format(job.jobId))
            self.cleanupJobDir(jobId)
            
            FileUtils.createDirectory(os.path.split(archivePath)[0])
            archive = Archive.packFolder(archivePath, jobDir)

            self.logger.info("Sending results of job {}".format(jobId))
            if not self.networkManager.sendFile(self.serverId, archive):
                self.logger.error("Could not transfer file {} to {}".format(archive, job.workstation))
                FileUtils.deleteFile(archive)
                return False
            else:
                if not self.debugMode:
                    FileUtils.clearDirectory(jobDir)
                    FileUtils.deleteFile(jobDir)

        FileUtils.deleteFile(archive)        
        return True

    def checkJobs(self):
        '''
        @summary: Checks all jobs which are saved in the database as 'RUNNING'
        @result:
        '''

        jobs = self.getFromDatabase(Job, stateId=JobState.lookup("RUNNING"))

        if jobs:
            for job in jobs:
                if not self.jobRunner.isRunning(job.jobId):
                    job.finished = datetime2Str(datetime.datetime.now())
                    job.stateId = JobState.lookup("ABORTED")
                    self.updateDatabaseEntry(job)

    def checkForPrograms(self, programs):
        '''
        @summary: Calls the WIM to check for the given programs
        @param programs: a list of dictionaries each containing a programName and
        a programExec
        @result:
        '''
        self.logger.info("Searching for program(s): {}".format(programs))
        self.wim.checkForPrograms(programs)
        self.sendWorkstationState()

    def fileReceived(self, pathToFile):
        '''
        @summary: Is called when a file was received successful
        @param pathToFile: path to the file
        @result:
        '''
        # The filename equals the job Id
        jobId = os.path.splitext(os.path.split(pathToFile)[1])[0]
        jobDir = os.path.join(self.workingDir, jobId)
        dest = os.path.join(jobDir, jobId)
        FileUtils.createDirectory(jobDir)
        FileUtils.copyFile(pathToFile, dest)
        Archive.unpack(dest)

        FileUtils.deleteFile(dest)
        reactor.callInThread(self.runJob, jobId)

    def createFileIndex(self, jobId):
        '''
        @summary: Creates a file index file in the job directory containing all files that are currently
        within the folder.
        @param jobId: the jobId for which the index should be created.
        @result:
        '''
        # Create a file list to decide which files are output.
        jobDir = os.path.join(self.workingDir, str(jobId))
        indexFilePath = os.path.join(jobDir, "index")

        files = os.listdir(jobDir)
        with open(indexFilePath, "w+") as indexFile:
            for f in files:
                indexFile.write(f + '\n')


    def cleanupJobDir(self, jobId):
        '''
        @summary: Cleans up the job directory of the given job and deletes all files which were send
        by the server (except log files) so only new (outputted) files remain.
        @param jobId:
        @result:
        '''
        if not self.debugMode:
            self.logger.info("Cleaning up job {}...".format(jobId))
            jobDir = os.path.join(self.workingDir, str(jobId))

            if not os.path.exists(jobDir):
                return

            indexFilePath = os.path.join(jobDir, 'index')
            files = []

            # Reading index file
            if os.path.exists(indexFilePath):
                with open(indexFilePath, 'r') as indexFile:
                    files = indexFile.readlines()

            self.logger.debug("Files to delete {}".format(len(files)))
            for f in files:
                filepath = os.path.join(jobDir, f).strip()
                self.logger.debug("Checking file {}".format(filepath))
                if os.path.isfile(filepath):
                    self.logger.debug("deleting file {}".format(filepath))
                    FileUtils.deleteFile(filepath)

            FileUtils.deleteFile(indexFilePath)

            for f in os.listdir(jobDir):
                filepath = os.path.join(jobDir, f).strip()
                if os.path.isfile(filepath):
                    newPath = os.path.join(jobDir, 'results', f)
                    FileUtils.moveFile(filepath, newPath)

    def updatePath(self, paths):
        '''
        @summary: Updates the program Path list.
        @param path: the new path
        @result: 
        '''
        self.logger.info("Updating search Paths: {}".format(paths))
        if paths:
            for p in paths:
                self.logger.debug("Adding {} to search Path".format(p))
                FileUtils.createOrAppendToFile(
                    os.path.join(self.workingDir, "PATHS"),
                    p + "\n")

            self.updatePathEnv(paths)

    def updatePathEnv(self, pathsToUpdate):
        paths = pathsToUpdate
        if not isinstance(paths, list):
            paths = [paths]

        for p in paths:
            current = os.environ['PATH']
            if not p.strip() in current:
                append = ":{}".format(p)
                append = append.strip()
                os.environ['PATH'] = os.environ['PATH'] + append

    def shutdown(self):
        '''
        @summary: Shuts the workstation down.
        @result: 
        '''
        self.logger.info("Shutting down...")
        self.stopWorkstationStateLoop()
        self.stopNetworkServices()
        reactor.stop()

    def getVersion(self):
        '''
        @summary: Returns the Version of the Software
        @result: 
        '''
        return VERSION


    # Misc
    # =====================================================
    def initializeLogger(self, workingDir, args):
        '''
        @summary: Initializes the logger
        @param workingDir:
        @param args:
        @result:
        '''
        self.logger = logging.getLogger("PySchedClient")
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level
        ch = logging.StreamHandler()
        if args.quiet:
            ch.setLevel(logging.ERROR)
        elif args.debug:
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')

        # create file handler and set level to debug
        logPath = os.path.join(self.workingDir, "log")
        with open(logPath, "w"):
            pass
        fh = logging.FileHandler(logPath)
        fh.setLevel(logging.INFO)

        # add formatter to ch
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def printTitle(self):
        '''
        @summary: Prints the title
        @result:
        '''
        print TITLE

