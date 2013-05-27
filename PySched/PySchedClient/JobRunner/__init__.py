# -*- coding: utf-8 -*-
'''
Created on 2012-12-20 15:08
@summary:
@author: Martin Predki
'''


from PySched.Common.Interfaces.JobRunnerInterface import JobRunnerInterface

from JobProcessProtocol import JobProcessProtocol

from twisted.internet import reactor

import os
import logging
import psutil

class JobRunner(JobRunnerInterface):
    '''
    @summary: Class that manages all processes
    '''
    def __init__(self, pySchedClient):
        '''
        @summary: Initializes a new JobRunner
        @param pySchedClient: A reference to the PySchedClient
        @result:
        '''
        self.pySchedClient = pySchedClient
        self.runningJobs = {}
        self.logger = logging.getLogger("PySchedClient")

    def runJob(self, job):
        '''
        @summary: Runs the given job.
        @param job: the job to run
        @result:
        '''
        try:
            # Setting up the process parameter
            # ==============================
            jobPath = os.path.join(self.pySchedClient.workingDir, str(job.jobId))

            # Adding job parameters
            # First parameter should be the executable name
            jobParams = job.executeStr.split(" ")
            self.logger.debug("Lookup program...")
            if jobParams[0] in job.reqPrograms:
                self.logger.debug("Searching program path")                
                programPath = self.pySchedClient.getProgramPath(jobParams[0])
                if programPath:
                    self.logger.debug("Path for {} found: {}".format(jobParams[0], programPath))
                    jobParams[0] = programPath
            else:
                self.logger.debug("Start program ({}) isn't required!".format(jobParams[0]))

            # Start the process
            # ==============================
            executable = os.path.join(jobPath, jobParams[0])
            self.logger.debug("Starting process: {executable} {args}".format(executable=executable, args=jobParams))

            protocol = JobProcessProtocol(job.jobId, jobPath, self)
            self.runningJobs[job.jobId] = protocol
            try:
                self.logger.debug("Environment: {}".format(os.environ))
                reactor.spawnProcess(protocol, executable=executable,
                    args=jobParams, path=jobPath, usePTY=True, env=os.environ)
            except Exception, e:
                self.logger.error(e)

            return True

        except Exception, e:
            self.logger.error("Failed to start job {}. Reason: {}".format(job.jobId, e))
            return False

    def abortJob(self, jobId):
        '''
        @summary: Aborts a job
        @param jobId:
        @result:
        '''
        process = self.runningJobs.get(jobId, None)

        if process:
            process.kill()

    def pauseJob(self, jobId):
        '''
        @summary: Pauses a job. 
        @param jobId:
        @result: True if the job is paused
        '''
        process = self.runningJobs.get(jobId, None)

        if process:
            pid = process.pid
            p = psutil.Process(pid)
            p.suspend()
            return True
        return False

    def resumeJob(self, jobId):
        '''
        @summary: Resumes the job with the given id
        @param jobId: the jobId
        @result: True if the job is resumed
        '''
        process = self.runningJobs.get(jobId, None)

        if process:
            try:                
                pid = process.pid                
                p = psutil.Process(pid)
                p.resume()
                return True
            except:
                return False
        return False    


    def jobStarted(self, jobId):
        '''
        @summary: Is called when a job is started.
        @param jobId: The started job
        @result: 
        '''
        self.logger.info("Job {} started.".format(jobId))
        self.pySchedClient.jobStarted(jobId)


    def jobCompleted(self, jobId):
        '''
        @summary: Is called when a job is completed.
        @param job: the completed job
        @result:
        '''
        self.logger.info("Job {} completed.".format(jobId))
        self.deleteRunningJob(jobId)

        self.pySchedClient.jobEnded(jobId, done=True)

    def jobFailed(self, jobId):
        '''
        @summary: Is called when a job failed.
        @param job: the completed job
        @result:
        '''
        self.logger.info("Job {} failed.".format(jobId))
        self.deleteRunningJob(jobId)

        self.pySchedClient.jobEnded(jobId, error=True)

    def jobAborted(self, jobId):
        '''
        @summary: Is called when a job is aborted.
        @param job: the aborted Job
        @result:
        '''
        self.logger.info("Job {} aborted.".format(jobId))
        self.deleteRunningJob(jobId)

        self.pySchedClient.jobEnded(jobId, aborted=True)

    def isRunning(self, jobId):
        '''
        @summary: Checks if the given job is currently running
        @param jobId:
        @result:
        '''
        if jobId in self.runningJobs:
            return True

        return False

    def deleteRunningJob(self, jobId):
        if jobId in self.runningJobs:
            del self.runningJobs[jobId]

    def getRunningJobCount(self):
        '''
        @summary: Returns the count of currently running jobs.
        @result: 
        '''
        return len(self.runningJobs)




