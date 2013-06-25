# -*- coding: utf-8 -*-
'''
Created on 2012-12-05 11:19
@summary:
@author: Martin Predki
'''

from PySched.Common.DataStructures import JobState
import logging

class SchedulerInterface(object):
    '''
    @summary: Base class for all scheduler implementations.
    '''
    def __init__(self, workingDir, pySchedServer):
        '''
        @summary:           Initializes the Scheduler class
        @param workingDir:  Path to the working directory of the pySchedServer.
                            All files and data should be saved within this 
                            folder.
        @param pySchedServer: A reference to the PySchedServer
        @result:
        '''
        self.logger = logging.getLogger("PySchedServer")
        self.workingDir = workingDir
        self.pySchedServer = pySchedServer

    def scheduleJob(self, workstations, job):
        '''
        @summary:           This function is called when a job should 
                            be scheduled.
        @param job:         The job to schedule
        @result:            Returns true if the job was scheduled successful. 
                            Else false and a String containing the function 
                            name that failed.
        '''
        if job.stateId < JobState.lookup("PREPARED"):
            self.logger.info("Preparing Job {}...".format(job.jobId))
            if not self.prepareJob(job):
                job.log("Failed to prepare Job.")
                self.logger.error("Failed to prepare Job {jobId}".format(jobId=job.jobId))
                job.stateId = JobState.lookup("SCHEDULER_ERROR")
                self.pySchedServer.updateDatabaseEntry(job)
                return False

        self.logger.info("Check job permissions for job {}...".format(job.jobId))
        if not self.checkJobPermission(job):
            job.log("Job has not the demanded permissions")
            self.logger.error("Can't run job {jobId}. Job permission denied.".format(jobId=job.jobId))
            job.stateId = JobState.lookup("PERMISSION_DENIED")
            self.pySchedServer.updateDatabaseEntry(job)
            return False

        self.logger.info("Check user permissions for job {}...".format(job.jobId))
        if not self.checkUserPermission(job):
            job.log("User has not the demanded permission")
            self.logger.error("Can't run job {jobId}. User permission denied".format(jobId=job.jobId))
            job.stateId = JobState.lookup("PERMISSION_DENIED")
            self.pySchedServer.updateDatabaseEntry(job)
            return False
            
        self.logger.info("Selecting workstation for job {}...".format(job.jobId))
        job.workstation = self.selectWorkstation(workstations, job)            

        if not job.workstation:
            self.logger.info("No appropriate Workstation for job {} found.".
                format(job.jobId))
            self.pySchedServer.addToJobLog(
                job.jobId,
                "No appropriate Workstation found.") 
            job.stateId = JobState.lookup("WAITING_FOR_WORKSTATION") 
            self.pySchedServer.updateDatabaseEntry(job)
            return False
        else:
            self.workstationSelected(job)

        self.logger.info("Compile Job {}...".format(job.jobId))
        if not self.compileJob(job):
            job.log("Failed to compile the Job.")
            self.logger.error("Failed to compile job {jobId}".format(jobId=job.jobId))
            job.stateId = JobState.lookup("COMPILER_ERROR")
            self.pySchedServer.updateDatabaseEntry(job)
            return False

        if job.stateId == JobState.lookup("COMPILED"):            
            if self.transferJob(job):
                job.stateId = JobState.lookup("DISPATCHED")
                self.pySchedServer.updateDatabaseEntry(job)
            else:
                job.stateId = JobState.lookup("SCHEDULER_ERROR")
                self.pySchedServer.updateDatabaseEntry(job)
        else:
            self.logger.info("Waiting for compiler...")

    def transferJob(self, job):
        '''
        @summary:           This function is called when the job is 
                            successful compilied.
        @param job:
        @result:            return true if the job was sent successful.
        '''
        if not job.workstation:
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
        @summary:           This is the first function to call in the 
                            schedule order.
                            Within this function all necessary files should be 
                            copied to the job directory. This function must be 
                            overridden.
        @param job:
        @result:            True if the job is prepared successful
        '''
        job.stateId = JobState.lookup("PREPARED")
        self.pySchedServer.updateDatabaseEntry(job)        
        return True

    def checkJobPermission(self, job):
        '''
        @summary:           This function should be used for all security checks
                            regarding the job. This function may be overridden.
        @param job:
        @result:            Return true if the job got the permission to run
        '''
        return True

    def checkUserPermission(self, job):
        '''
        @summary:           This function should be used for all security 
                            checks regarding the user. This function may be 
                            overridden
        @param job:
        @result:            Return True if the user got the permission to run
                            the job
        '''
        return True

    def selectWorkstation(self, workstations, job):
        '''
        @summary:           This function should contains the scheduling logic.
                            It must be overridden
        @param workstations: A list of dictionaries containing the currently 
                            available workstations.
                            For further informations about the contents of the 
                            dictionary, see the 
                            Common.Interfaces.WorkstationReference.
        @param job:
        @result:            A reference or id of the workstation.
        '''
        raise NotImplementedError

    def workstationSelected(self, job):
        '''
        @summary:           This function is called, after a workstation is
                            selected. It can be used to reserve a Resource for
                            a job, before it is transferred.
        @param job: the job
        @result: 
        '''
        pass 


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
        self.pySchedServer.updateDatabaseEntry(job)
        return True        

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

    def updateSchedulingParameter(self, parameter):
        '''
        @summary: This function can be called by the PySchedServer, if a user
        wants to update the scheduling parameters. This function is optional
        for the scheduling algorithm. The standard implementation of the
        scheduling algorithm supports values for a free cpu threshold, the 
        penality for unused cores / programs and how many cpu should be reserverd
        for users on the workstation.
        @param parameter: parameter is a dictionary containing the new parameters
        @result: 
        '''
        pass

    def getSchedulingParameter(self):
        '''
        @summary: This function should return a dictionary of the current
        Scheduling parameters. This function is optional
        @result: 
        '''
        pass

    def jobAborted(self, jobId):
        '''
        @summary: This function is called, when the user aborts or deletes a job
        that is currently in the scheduling queue
        @param jobId: the id of the job
        @result: 
        '''
        pass
