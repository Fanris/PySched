# -*- coding: utf-8 -*-
'''
Created on 2013-01-04 12:10
@summary:
@author: Martin Predki
'''

from twisted.internet import reactor

from CompilerProcessProtocol import CompilerProcessProtocol

import logging
import os

class Compiler(object):
    '''
    @summary: Class containing the compile logic for jobs.
    '''

    def __init__(self, scheduler):
        '''
        @summary: Initializes the compiler.
        @param scheduler: A reference to the scheduler
        @result:
        '''
        self.scheduler = scheduler
        self.logger = logging.getLogger("PySchedServer")


    def compileJob(self, job):
        '''
        @summary: Compiles a job.
        @param job:
        @result:
        '''

        # Setting up the compile process parameter
        # ==============================
        jobPath = os.path.join(self.scheduler.workingDir, str(job.jobId))

        # parse command Template
        template = job.compilerStr.split(" ")

        # Start the compiler
        # ==============================

        self.logger.debug("Spawn process: {}".format(template))

        reactor.spawnProcess(CompilerProcessProtocol(job, jobPath, self.scheduler), executable=template[0],
            args=template, path=jobPath, env=os.environ)

        # write a log file
        # ==============================
        self.logger.info("Compile process for job {} started.".format(job.jobId))
        return True

    def compilingCompleted(self, job):
        '''
        @summary: Is called when a job is compiled successful.
        @param job:
        @result:
        '''
        self.scheduler.compilingComplete(job)

    def compilingFailed(self, job):
        '''
        @summary: Is called when a job could not be compiled
        @param job:
        @result:
        '''
        self.scheduler.compilingFailed(job)

