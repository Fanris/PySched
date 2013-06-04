#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 10.08.2012

PySched-Server. PySched-Server is used to run various Programs on remote
Workstations.

@author: Martin Predki
'''

from PySched.Common.Communication.CommandBuilder import CommandBuilder
from PySched.Common.DataStructures import Job, User, JobState, Program
from PySched.Common import datetime2Str
from PySched.Common.IO import FileUtils
from PySched.Common.IO import Archive

from DatabaseManagement import SqliteManager
from Scheduler import PyScheduler
from NetworkManagement import NetworkManager
from MessageHandler import MessageHandler

from twisted.internet import reactor

import psutil

import platform
import logging
import datetime
import os


VERSION = "1.2.5"
TITLE = """
 _____        _____      _              _  _____                           
|  __ \      / ____|    | |            | |/ ____|                          
| |__) |   _| (___   ___| |__   ___  __| | (___   ___ _ ____   _____ _ __  
|  ___/ | | |\___ \ / __| '_ \ / _ \/ _` |\___ \ / _ \ '__\ \ / / _ \ '__| 
| |   | |_| |____) | (__| | | |  __/ (_| |____) |  __/ |   \ V /  __/ |    
|_|    \__, |_____/ \___|_| |_|\___|\__,_|_____/ \___|_|    \_/ \___|_|    
        __/ |                              Copyright 2012 by Martin Predki 
       |___/                               Version {}          

==========================================================================
""".format(VERSION)


class PySchedServer(object):
    def __init__(self, workingDir, args):
        '''
        @summary: Initializes the PySchedServer.
        @param workingDir: Path to the main directory to work on
        '''
        self.workingDir = os.path.normpath(workingDir)
        FileUtils.createDirectory(workingDir)

        self.initializeLogger(self.workingDir ,args)
        if not args.quiet:
            self.printTitle()

        self.logger.info("Starting PySchedServer v{}".format(VERSION))

        self.dbController = SqliteManager(self.workingDir)
        self.scheduler = PyScheduler(self.workingDir, self)
        
        self.networkManager = NetworkManager(
            self.workingDir, 
            MessageHandler(self),
            multiGroup=args.multicast)

        self.workstations = {}

        self.networkManager.startService()
        reactor.run()

    # Database Functions
    # ========================
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
        returnList = filter(self.createFilterFunction(**filterArgs), objects)

        if first:
            if len(returnList) == 0:
                return None
            return returnList[0]

        return returnList

    def updateDatabaseEntry(self, obj):
        '''
        @summary: Updates the entry within the database
        @param obj: the object to update
        @result:
        '''
        return self.dbController.updateDatabaseEntry(obj)

    def deleteFromDatabase(self, obj):
        '''
        @summary: Deletes the given object from the database
        @param obj:
        @result:
        '''
        self.dbController.deleteFromDatabase(obj)


    def createFilterFunction(self, **filterArgs):
        '''
        @summary: Creates a function from filterArgs to be used in
        a filter.
        @param **filterArgs:
        @result:
        '''
        def checkItem(item):
            for key, value in filterArgs.iteritems():
                if str(getattr(item, key, None)) != str(value):
                    return False

            return True
        return checkItem


    # Scheduling Functions
    # ========================
    def schedule(self, jobId=None):
        '''
        @summary: Starts scheduling.
        @result:
        '''
        if not jobId:
            jobs = self.getFromDatabase(Job)
            for job in jobs:
                self.schedule(job.jobId)
        else:
            job = self.getFromDatabase(Job, jobId=jobId, first=True)
            if job:
                if job.stateId == JobState.lookup("WAITING_FOR_WORKSTATION") or \
                    job.stateId == JobState.lookup("QUEUED") or \
                    job.stateId == JobState.lookup("PREPARED"):
                        self.scheduler.scheduleJob(job=job, 
                            workstations=self.workstations.values())
                        self.addToJobLog(job.jobId, "Job scheduled.")

    # Job Functions
    # ========================
    def addJob(self, jobInformations):
        '''
        @summary: Adds a Job to the database
        @param jobInformations: Dictionary with job informations
        @result: Returns true if the job was added successful.
        '''
        job = Job()
        job.added = datetime2Str(datetime.datetime.now())

        for key in jobInformations:
            if key in job.__dict__:
                setattr(job, key, jobInformations[key])
            else:
                job.otherAttr[key] = jobInformations[key]

        self.logger.debug("New Job: {}".format(job.__dict__))

        user = self.getFromDatabase(User, userId=jobInformations.get("userId", ""), first=True)
        if not user:
            return False

        job.userId = user.id

        job = self.addToDatabase(job)
        if job:
            jobDir = FileUtils.createDirectory(os.path.join(self.workingDir, str(job.jobId)))
            FileUtils.createDirectory(os.path.join(jobDir, "logs"))
            self.addToJobLog(job.jobId, "Job added.")
            return job

        return False

    def updateJobState(self, jobInformations):
        '''
        @summary: updates the jobInformations
        @param jobInformations: A dictionary containing the job informations.
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobInformations.get("jobId", ""), first=True)
        isDeleted = False
        if job.stateId == JobState.lookup("DELETED"):
            isDeleted = True

        if job:            
            self.logger.info("Updating job state of job {}".format(job.jobId))
            for key in jobInformations:
                if key in job.__dict__:
                    value = jobInformations.get(key, None)
                    if value != None and value != "":
                        setattr(job, key, value)
                else:
                    job.otherAttr[key] = jobInformations[key]

        self.updateDatabaseEntry(job)
        if job.stateId >= JobState.lookup("DONE"):
            self.logger.info("Job {} ended with state {}.".format(
                job.jobId, JobState.lookup(job.stateId)))
            self.cleanupJobDir(job.jobId)
            self.getResultsFromWorkstation(job.jobId)    
            self.addToJobLog(job.jobId, "Job Ended.")        
            reactor.callInThread(self.schedule)

        if isDeleted:
            job.JobState = JobState.lookup("DELETED")
            self.updateDatabaseEntry(job)

    def killJob(self, jobId, userId):
        '''
        @summary: Kills a job.
        @param jobId: Id of the job to kill.
        @param userId: userId of the user who requested this.
        @result: Returns true if the kill signal is sent to
        the workstation
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        user = self.getFromDatabase(User, userId=userId, first=True)

        if not (job or user) or not (job.userId == user.id):
            return False

        job.stateId = JobState.lookup("ARBORTED")
        self.updateDatabaseEntry(job)
        networkId = self.lookupWorkstationName(job.workstation)
        self.logger.info("Aborting job {} on workstation {} ({})".format(job.jobId, job.workstation, networkId))
        self.networkManager.sendMessage(networkId, CommandBuilder.buildKillJobString(job.jobId))    
        self.addToJobLog(job.jobId, "Job aborted by user.")  
        return True  

    def deleteJob(self, userId, jobId):
        '''
        @summary: Deletes a the given job of the given user.
        @param userId: the owner of the job.
        @param jobId: the jobId
        @result:
        '''
        self.logger.info("Deleting Job {}...".format(jobId))
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        user = self.getFromDatabase(User, userId=userId, first=True)

        if not (job or user) or not (job.userId == user.id):
            return False

        if job.stateId == JobState.lookup("RUNNING"):
            self.killJob(jobId, userId)

        self.logger.info("Deleting job {} from database.".format(jobId))
        self.cleanupJobDir(jobId)
        job.stateId = JobState.lookup("DELETED")
        self.updateDatabaseEntry(job)

        return True

    def transferJob(self, job):
        '''
        @summary: Transfers a job to the selected Client.
        All files within the job folder are packed and transferred
        @param job: The job to transfer.
        @result:
        '''
        jobDir = os.path.join(self.workingDir, str(job.jobId))
        archivePath = os.path.join(self.workingDir, "temp", "{}.tar".format(job.jobId))
        FileUtils.createDirectory(os.path.split(archivePath)[0])
        archive = Archive.packFolder(archivePath, jobDir)
        networkId = self.lookupWorkstationName(job.workstation)

        self.networkManager.sendMessage(networkId, CommandBuilder.buildAddJobString(**job.__dict__))

        if not self.networkManager.sendFile(networkId, archive):
            self.logger.error("Could not transfer file {} to {}".format(archive, job.workstation))
            FileUtils.deleteFile(archive)
            return False
        else:
            FileUtils.clearDirectory(jobDir, deleteSubfolders=False)

        self.addToJobLog(job.jobId, "Job sent to Workstation {}".format(job.workstation))
        FileUtils.deleteFile(archive)
        return True

    def cleanupJobDir(self, jobId):
        '''
        @summary: Removes all files from the job directory.
        @param jobId:
        @result:
        '''
        jobDir = os.path.join(self.workingDir, str(jobId))
        FileUtils.clearDirectory(jobDir)
        FileUtils.deleteFile(jobDir)

    def archiveJob(self, jobId):
        '''
        @summary: Archives a job
        @param jobId: the job id
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)

        if job:
            job.stateId += 90
            self.updateDatabaseEntry(job)
            self.cleanupJobDir(job.jobId)
            self.addToJobLog(job.jobId, "Job Archived.")
            self.logger.info("Job {} Archived: {}".format(job.jobId, 
                JobState.lookup(job.stateId)))
            return True
        else:
            return False

    def addToJobLog(self, jobId, message):
        job = self.getFromDatabase(Job, jobId=jobId, first=True)

        if job:
            logPath = os.path.join(self.workingDir, str(jobId), "logs", "joblog.log")
            m = "[{}] {}\n".format(datetime2Str(datetime.datetime.now()),
                message)
            FileUtils.createOrAppendToFile(logPath, m)

    def getJob(self, jobId):
        job = self.getFromDatabase(Job, first=True, jobId=jobId)

        return job

    def reserveCPU(self, job):
        self.logger.info("Reserving CPU for job {} on {}".format(
            job.jobId,
            job.workstation))
        networkId = self.lookupWorkstationName(job.workstation)
        self.networkManager.sendMessage(networkId,
            CommandBuilder.buildReserveCPUString(job.jobId))

    def pauseJob(self, userId, jobId):
        self.logger.info("Try to pause job {}".format(jobId))
        user = self.getUser(userId)
        job = self.getJob(jobId)

        if (job and user) and \
            (job.userId == user.id or user.admin):
            networkId = self.lookupWorkstationName(job.workstation)
            self.networkManager.sendMessage(networkId,
                CommandBuilder.buildPauseJobString(job.jobId))            

    def resumeJob(self, userId, jobId):
        self.logger.info("Try to resume job {}".format(jobId))
        user = self.getUser(userId)
        job = self.getJob(jobId)

        if (job and user) and \
            (job.userId == user.id or user.admin):
            networkId = self.lookupWorkstationName(job.workstation)
            self.networkManager.sendMessage(networkId,
                CommandBuilder.buildResumeJobString(job.jobId))            

    # User Functions
    # ========================
    def createUser(self, userInformation):
        '''
        @summary: Creates a new user with the given informations.
        @param firstName: The first name
        @param lastName: The last name
        @param email: The email address
        @result: Return an generated userId
        '''
        u = User()
        for key in userInformation:
            if key in u.__dict__:
                setattr(u, key, userInformation[key])
            else:
                u.otherAttr[key] = userInformation[key]

        u.userId = u.email

        user = self.getFromDatabase(User, userId=u.userId, first=True)

        if user:
            result = self.updateDatabaseEntry(u)
        else:
            result = self.addToDatabase(u)

        if not result:
            return False

        return True

    def getUser(self, userId):
        '''
        @summary: Returns the user object for the given userId
        @param userId: The userId to check.
        @result: 
        '''
        if not userId:
            return None

        return self.getFromDatabase(User, first=True, userId=userId)

    def getJobList(self, userId, showAll, showAllUser):
        '''
        @summary: Returns a list with all jobs of the user
        @param userId: the user id
        @param showAll: show all Jobs including archived
        @result:
        '''
        user = self.getFromDatabase(User, userId=userId, first=True)
        if not user:
            return False

        jobs = []
        if user.admin and showAllUser:
            jobs = self.getFromDatabase(Job)
        else:
            jobs = self.getFromDatabase(Job, userId=user.id)

        returnList = []
        for i in range(0, len(jobs)):
            if (showAll and jobs[i].stateId >= JobState.lookup("ARCHIVED")) or \
               (jobs[i].stateId < JobState.lookup("ARCHIVED")):
                returnList.append(jobs[i])

        return returnList

    def returnResultsToClient(self, userId, jobId):
        '''
        @summary: Returns the results of the given job
        @param userId: the userId of the job owner.
        @param jobId: the id of the job.
        @result:
        '''
        self.logger.info("Retrieving results of job {}".format(jobId))
        job = self.getFromDatabase(Job, jobId=jobId, first=True)
        user = self.getFromDatabase(User, userId=userId, first=True)

        if not job or not user or not job.userId == user.id:
            self.logger.info("Could not retrieve results for job {}".format(jobId))
            return False

        jobDir = os.path.join(self.workingDir, str(job.jobId))
        archivePath = os.path.join(self.workingDir, "temp", "{}_{}_results.tar".format(job.jobId, job.jobName))
        FileUtils.createDirectory(os.path.split(archivePath)[0])
        archive = Archive.packFolder(archivePath, jobDir)
        self.logger.info("Results for job {} prepared.".format(jobId))
        return archive  

    def getLog(self, jobId, userId):
        '''
        @summary: Reads the logfile of a job and returns it
        @param jobId: the jobId of the job
        @param userId: the user id of the requesting user
        @result: 
        '''
        user = self.getUser(userId)
        job = self.getJob(jobId)

        if user.id == job.userId or user.admin:
            logPath = os.path.join(self.workingDir, str(jobId), "logs", "joblog.log")            
            log = ""
            for bytes in FileUtils.readBytesFromFile(logPath):
                log += bytes

            return log

    def addProgram(self, userId, program):
        '''
        @summary: Adds a new program to the database
        @param userId: The user who sends the request
        @param program: the new program
        @result: 
        '''
        user = self.getUser(userId)

        if user.admin:
            programs = self.getFromDatabase(Program)
            for p in programs:
                if p.programName == program.programName and \
                    p.programVersion == program.programVersion:

                    program.id = p.id
                    if self.updateDatabaseEntry(p):
                        return True
                    else:
                        return False
            if self.addToDatabase(program):
                return True

        return False

    # Workstation Functions
    # ========================
    def addWorkstation(self, networkId, workstationInfo):
        '''
        @summary: Adds a new workstation to the list.
        @param networkId: the networkId
        @result:
        '''
        newMachineName = workstationInfo.get("workstationName", None)
        if not newMachineName:
            self.logger.warning("Try to add a Workstation with no name.")

        for k, v in self.workstations.iteritems():
            if v.get("workstationName", None) == newMachineName:
                self.logger.debug("Overriding old workstation Informations")
                del self.workstations[k]

        self.workstations[networkId] = workstationInfo
        self.logger.info("New workstation {} added. Currently are {} workstations available."
            .format(workstationInfo.get("workstationName", None), len(self.workstations)))

        self.logger.info("Sending global search Paths to workstation")
        self.sendSearchPaths(workstationInfo.get("workstationName", None))

        self.logger.info("Checking programs on workstation {}".format(workstationInfo.get("workstationName", None)))
        self.checkForPrograms(workstationInfo.get("workstationName"))

        self.logger.info("Checking Jobs of workstation {}".format(workstationInfo.get("workstationName", None)))
        self.checkJobs(workstationInfo.get("workstationName", None))

        reactor.callInThread(self.schedule)

    def updateWorkstation(self, networkId, workstationInfo):
        '''
        @summary: Updates the workstation informations.
        @param workstationInfo: the new informations.
        @result:
        '''
        if not networkId in self.workstations:
            self.addWorkstation(networkId, workstationInfo)
        else:
            self.workstations[networkId].update(workstationInfo)

    def removeWorkstation(self, networkId):
        '''
        @summary: Removes the workstation with the networkId from the list
        @param networkId: the networkId to remove
        @result:
        '''
        if networkId in self.workstations:
            self.logger.info("Connection to workstation {} lost.".format(self.lookupNetworkId(networkId).get("workstationName")))
            del self.workstations[networkId]            

    def getWorkstations(self):
        '''
        @summary: Returns all currently registered workstations
        @result: a list of workstations (dictionaries containing the workstation informations)
        '''
        return self.workstations.values()

    def lookupWorkstationName(self, workstationName):
        '''
        @summary: Takes a machine name and search for a registered network client
        @param workstationName: the name to look up
        @result:
        '''
        for k, v in self.workstations.iteritems():
            if v.get("workstationName", None) == workstationName:
                return k

    def lookupNetworkId(self, networkId):
        '''
        @summary: Takes a networkId and search for a registered workstation
        @param workstationName: the networkId to look up
        @result:
        '''
        return self.workstations.get(networkId, None)        

    def getJobCountOnWorkstation(self, workstation):
        '''
        @summary: Returns the count of running jobs on the workstation
        @param workstation: the workstation to check
        @result: count of running jobs on the workstation
        '''
        if not workstation:
            return 0

        jobs = self.getFromDatabase(Job, workstation=workstation)

        runningJobs = 0
        for job in jobs:
            if job.stateId == JobState.lookup("RUNNING"):
                runningJobs += 1

        return runningJobs

    def checkForPrograms(self, workstation, programs=[]):
        '''
        @summary: Checks the workstation for the programs defined in the database.
        @param workstation: the workstation which should be checked
        @param programs: a List of program names to check for.
        @param waitForAnswer: Wait 5 second for an answer
        @result:
        '''
        progs = self.getFromDatabase(Program)
        if not isinstance(progs, list):
            progs = [progs]

        checkFor = programs
        if progs:
            checkFor.extend(progs)

        if len(checkFor) > 0:
            temp = [x.__dict__ for x in checkFor]

            networkId = self.lookupWorkstationName(workstation)

            self.networkManager.sendMessage(networkId, 
                CommandBuilder.buildCheckForProgramsString(temp))    

    def checkJobs(self, workstation=None):
        '''
        @summary: Checks all Jobs which are not in an end state and
        updates them if necessary.
        @result:
        '''
        jobs = self.getFromDatabase(Job)

        for job in jobs:
            if job.stateId == JobState.lookup("RUNNING"):
                if not workstation or workstation == job.workstation:
                    networkId = self.lookupWorkstationName(job.workstation)
                    self.logger.debug("Sending getJobState command for Job {} to workstation {}".format(job.jobId, job.workstation))
                    self.networkManager.sendMessage(networkId, CommandBuilder.buildGetJobStateString(job.jobId))
            elif job.stateId >= JobState.lookup("DONE") and job.stateId < JobState.lookup("ARCHIVED"):
                if not os.path.exists(os.path.join(self.workingDir, str(job.jobId), 'results')):
                    self.getResultsFromWorkstation(job.jobId)
    
    def getResultsFromWorkstation(self, jobId):
        '''
        @summary: Is called to return the results of the given job from the workstation
        @param jobId: the id of the job
        @result:
        '''
        job = self.getFromDatabase(Job, jobId=jobId, first=True)

        if job and job.stateId >= JobState.lookup("DONE") \
            and job.stateId < JobState.lookup("SCHEDULER_ERROR"):
            self.logger.info("Requesting results for job {} from {}".format(jobId, job.workstation))
            networkId = self.lookupWorkstationName(job.workstation)
            self.networkManager.sendMessage(networkId, CommandBuilder.buildGetResultsString(job.jobId))
            return True
        else:
            return False

    def sendSearchPaths(self, workstationName):
        '''
        @summary: Sends the configured search path to the workstation
        @param workstation:
        @result: 
        '''
        paths = self.getPath()
        if paths and len(paths) > 0:
            networkId = self.lookupWorkstationName(workstationName)
            if networkId:
                self.networkManager.sendMessage(
                    networkId,
                    CommandBuilder.buildUpdatePathString(paths))


    # FileTransfer Functions
    # ========================
    def fileReceived(self, pathToFile):
        '''
        @summary: Is called when a file was received successful
        @param pathToFile: path to the file
        @result:
        '''
        # The filename equals the job Id
        jobId = os.path.splitext(os.path.split(pathToFile)[1])[0]
        dest = os.path.join(self.workingDir, jobId, jobId)
        FileUtils.copyFile(pathToFile, dest)

        job = self.getJob(jobId)
        # Check if job currently running        
        if job.stateId < JobState.lookup("DONE") and \
            job.stateId >= JobState.lookup("RUNNING"):
            self.logger.info("Updating job data of {}".format(jobId))
            networkId = self.lookupWorkstationName(job.workstation)
            if networkId:
                self.networkManager.sendFile(networkId, dest)
                FileUtils.deleteFile(dest)
        else:
            self.logger.info("Unpacking file...")
            Archive.unpack(dest)

            if job.stateId < JobState.lookup("PREPARED"):
                reactor.callInThread(self.schedule, jobId)

        FileUtils.deleteFile(dest)
        FileUtils.deleteFile(pathToFile)
        return True

    def fileTransferFailed(self, pathToFile):
        '''
        @summary: Is called when a file transfer has failed due to invalid md5 hashsum
        @param pathToFile: path to the file
        @result:
        '''
        self.logger.error("Failed to receive {}".format(pathToFile))
        jobId = os.path.splitext(os.path.split(pathToFile)[1])[0]
        job = self.getFromDatabase(Job, jobId=jobId, first=True)

        if job and job.stateId < JobState.lookup("RUNNING"):
            self.deleteFromDatabase(job)        

    # Internal Functions
    # ========================

    def stopAll(self, userId):
        '''
        @summary: Shuts down all Workstations and the server
        @param userId:
        @result: 
        '''
        user = self.getUser(userId)
        if user.admin:
            for networkId in self.workstations.keys():
                self.logger.info("Shutting down {}".format(
                    self.lookupNetworkId(networkId).get("workstationName", "")))
                self.networkManager.sendMessage(
                    networkId, 
                    CommandBuilder.buildShutdownString())

        reactor.callLater(10, self.shutdown)

    def shutdown(self):
        '''
        @summary: Shut the server down.
        @result: 
        '''
        self.logger.info("Shutting down...")
        self.networkManager.stopService()
        reactor.stop()

    def getServerInformations(self):
        '''
        @summary: Uses psutils to get Informations of the Server.
        @result: 
        '''
        server = {}
        server.update({
            "os": platform.system(),
            "workstationName": "Server ({})".format(platform.node()),
            "machine": platform.machine(),
            "cpuCount": psutil.NUM_CPUS,
            "memory": psutil.virtual_memory()[0] / (1024**3),
            "diskAvailable": psutil.disk_usage(
                self.workingDir)[0] / (1024**3),      
            "diskLoad": psutil.disk_usage(self.workingDir)[3],
            "diskFree": psutil.disk_usage(self.workingDir)[2] / (1024**3),
            "version": VERSION,
            })

        return server

    def appendPath(self, userId, path):        
        user = self.getUser(userId)
        if user.admin:
            self.logger.info("Adding a new search path: {}".format(path))
            FileUtils.createOrAppendToFile(
                os.path.join(self.workingDir, "PATHS"),
                path + "\n")

            for networkId in self.workstations.keys():
                self.networkManager.sendMessage(
                    networkId,
                    CommandBuilder.createUpdatePathString([path]))

    def getPath(self):
        return FileUtils.readFile(os.path.join(self.workingDir, "PATHS"))

    def lookupUserId(self, userRealId):
        '''
        @summary:       Searches the username for the given userId (database)
        @param userId:
        @result: 
        '''
        return self.getFromDatabase(User, first=True, id=userRealId)


    def initializeLogger(self, workingDir, args):
        '''
        @summary: Initializes the logger
        @param workingDir:
        @param args:
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
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
        @summary: Prints the Title
        @result:
        '''
        print TITLE
