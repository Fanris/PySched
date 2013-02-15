# -*- coding: utf-8 -*-
'''
Created on 2012-12-05 11:19
@summary:
@author: Martin Predki
'''

from Common.DataStructures import JobState
import logging

class SchedulerInterface(object):
    '''
    @summary: Base class for all scheduler implementations.
    '''
    def __init__(self, workingDir, pySchedServer):
        '''
        @summary: Initializes the Scheduler class
        @param workingDir: Path to the working directory of the pySchedServer.
        All files and data should be saved within this folder.
        @param pySchedServer: A reference to the PySchedServer
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
        self.workingDir = workingDir
        self.pySchedServer = pySchedServer

    def scheduleJob(self, workstations, job):
        '''
        @summary: This function is called when a job should be scheduled.
        @param job: The job to schedule
        @result: Returns true if the job was scheduled successful. Else
        false and a String containing the function name that failed.
        '''
        self.logger.info("Preparing Job {}...".format(job.jobId))
        if not self.prepareJob(job):
            self.logger.error("Failed to prepare Job {jobId}".format(jobId=job.jobId))
            job.stateId = JobState.lookup("SCHEDULER_ERROR")
            return False

        self.logger.info("Check job permissions for job {}...".format(job.jobId))
        if not self.checkJobPermission(job):
            self.logger.error("Can't run job {jobId}. Job permission denied.".format(jobId=job.jobId))
            job.stateId = JobState.lookup("PERMISSION_DENIED")
            return False

        self.logger.info("Check user permissions for job {}...".format(job.jobId))
        if not self.checkUserPermission(job):
            self.logger.error("Can't run job {jobId}. User permission denied".format(jobId=job.jobId))
            job.stateId = JobState.lookup("PERMISSION_DENIED")
            return False

        self.logger.info("Compile Job {}...".format(job.jobId))
        if not self.compileJob(job):
            self.logger.error("Failed to compile job {jobId}".format(jobId=job.jobId))
            job.stateId = JobState.lookup("COMPILER_ERROR")
            return False

        self.logger.info("Selecting workstation for job {}...".format(job.jobId))
        job.workstation = self.selectWorkstation(workstations, job)

        if job.stateId == JobState.lookup("COMPILED"):
            if self.transferJob(job):
                job.stateId = JobState.lookup("DISPATCHED")
            else:
                job.stateId = JobState.lookup("SCHEDULER_ERROR")
        else:
            self.logger.info("Waiting for compiler...")

    def transferJob(self, job):
        '''
        @summary: This function is called when the job is successful compilied.
        @param job:
        @result: return true if the job was sent successful.
        '''
        if not job.workstation:
            self.logger.warning("Failed to schedule job {}. No appropriate workstation found.".format(job.jobId))
            return False

        self.logger.info("Preparing job {}".format(job.jobId))
        if not self.prepareForTransfer(job):
            self.logger.error("Failed to prepare job {} for transmission.".format(job.jobId))
            return False


        self.logger.info("Transfer job {} to {}".format(job.jobId, job.workstation))
        if not self.transfer(job):
            self.logger.error("Failed to transfer job {} to workstation {}".format(job.jobId, job.workstation))
            return False

        return True

    def prepareJob(self, job):
        '''
        @summary: This is the first function to call in the schedule order.
        Within this function all necessary files should be copied to the job
        directory. This function must be overridden.
        @param job:
        @result: True if the job is prepared successful
        '''
        job.stateId = JobState.lookup("PREPARED")
        return True

    def checkJobPermission(self, job):
        '''
        @summary: This function should be used for all security checks
        regarding the job. This function may be overridden.
        @param job:
        @result: Return true if the job got the permission to run
        '''
        return True

    def checkUserPermission(self, job):
        '''
        @summary: This function should be used for all security checks
        regarding the user. This function may be overridden
        @param job:
        @result: Return True if the user got the permission to run the job
        '''
        return True

    def compileJob(self, job):
        '''
        @summary: This function should be used to compile the job if necessary.
        If the job dont need to be compiled it should just return True.
        This function may be overridden if the scheduler should support
        compiling.
        @param job:
        @result: True if the job is compiled successful or doesn't need
        to be compiled.
        '''
        job.stateId = JobState.lookup("COMPILED")
        return True

    def selectWorkstation(self, workstations, job):
        '''
        @summary: This function should contains the scheduling logic.
        It must be overridden
        @param workstations: A list of dictionaries containing the currently available workstations.
        For further informations about the contents of the dictionary, see the Common.Interfaces.WorkstationReference.
        @param job:
        @result: A reference or id of the workstation.
        '''
        raise NotImplementedError

    def prepareForTransfer(self, job):
        '''
        @summary: This function should be used for transfer preparation
        of the job. E.g. packing of all needed files to reduce the transfer
        overhead. This function may be overridden
        @param job:
        @result: Return true if the preparation was successful
        '''
        return True

    def transfer(self, job):
        '''
        @summary: This is the final function in the schedule order. Here
        the PySchedServer is called to transfer the given file(s).
        This function must be overridden
        @param job:
        @result: return true if the job was sent successful.
        '''
        raise NotImplementedError
