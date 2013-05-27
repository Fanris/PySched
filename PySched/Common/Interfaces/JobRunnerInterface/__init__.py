# -*- coding: utf-8 -*-
'''
Created on 2013-01-15 11:14
@summary:
@author: Martin Predki
'''

class JobRunnerInterface(object):
    '''
    @summary: Interface class that defines all methods that need to be implemented
    in a Job Runner class. A Job Runner is used to run the jobs on the workstation
    '''

    def runJob(self, job):
        '''
        @summary: Runs the given job
        @param job: the job to run
        @result:
        '''
        raise NotImplementedError

    def abortJob(self, jobId):
        '''
        @summary: Aborts the job with the given id
        @param jobId: the jobId
        @result:
        '''
        raise NotImplementedError

    def pauseJob(self, jobId):
        '''
        @summary: Pauses the job with the given id
        @param jobId: the jobId
        @result:
        '''
        raise NotImplementedError

    def resumeJob(self, jobId):
        '''
        @summary: Resumes the job with the given id
        @param jobId: the jobId
        @result:
        '''
        raise NotImplementedError        

    def isRunning(self, jobId):
        '''
        @summary: Checks if the job with the given id is currently running.
        @param jobId: the job id
        @result:
        '''
        raise NotImplementedError





