# -*- coding: utf-8 -*-
'''
Created on 2012-12-05 11:59
@summary: Standard scheduler implementation.
@author: Martin Predki
'''

from PySched.Common.Interfaces.SchedulerInterface import SchedulerInterface
from PySched.Common.DataStructures import JobState

from Compiler import Compiler as CompilerClass

import logging

class PyScheduler(SchedulerInterface):
    '''
    @summary: Standard scheduler implementation.
    '''
    def __init__(self, workingDir, pySchedServer):
        '''
        @summary: Initializes the Scheduler
        @param workingDir: path to the working directory
        @param pySchedServer: Reference to the PySchedServer
        @result:
        '''
        super(PyScheduler, self).__init__(workingDir, pySchedServer)
        self.compiler = CompilerClass(self)
        self.logger = logging.getLogger("PySchedServer")

    def checkJobPermission(self, job):
        return True

    def checkUserPermission(self, job):
        return True

    def compileJob(self, job):
        if job.compilerStr == None or job.compilerStr == "":
            self.logger.info("No compiler needed.")
            job.stateId = JobState.lookup("COMPILED")
            return True

        if not self.compiler.compileJob(job):
            return False

        return True

    def selectWorkstation(self, workstations, job):
        if len(workstations) == 0:
            return None

        # For normal jobs select the workstation with the least amount of
        # free cpus.

        # For jobs with enabled multiprocessor support, select a workstation
        # with at least two free cpu's

        # For jobs with an minimum required count of cpus select an workstation
        # that fit to these requirements

        # Same for jobs with minimum required memory
        scores = {}
        for workstation in workstations:
            self.logger.debug("Checking workstation {}".format(workstation))
            freeCpus = 0
            # First check the installed OS
            if not workstation.get("os", None) == job.reqOS:
                continue

            for load in workstation.get("cpuLoad", []):
            # Count free cpus. Threshold of a free cpu is 20%
                if load < 20:
                    freeCpus += 1

            self.logger.debug("Free cpu count: {}".format(freeCpus))
            # when no cpu is free, this workstation should not
            # be considered any further
            if freeCpus == 0:
                continue

            # when the workstation has not the required amount of
            # memory, it should not be considered any further
            if job.minMemory > workstation.get("memory", 0) * 1024:
                continue

            # Check for programs
            for program in job.reqPrograms:
                if type(program) != type({}):
                    continue

                self.logger.debug("Check workstation for Program: {}.".format(program))
                p = filter(
                    lambda x: x.get("programName", None) ==
                        program.get("programName", None) and
                        x.get("programVersion", None) ==
                        program.get("programVersion", None),
                        workstation.get("programs")
                    )
                if p.count == 0:
                    break

            score = 0
            # If someone working on the machine the scheduler
            # should select another one first.
            if workstation.get("activeUsers", 0) > 0:
                score -= 100

            if job.multiCpu:
                # If the job supports multiple cpus, every free cpu
                # is valuable
                score += 100 * freeCpus
            else:
                # If not, workstations which are already occupied by
                # jobs should be selected, so other workstations might
                # be available for multiprocessor jobs
                score -= 100 * freeCpus

            scores[workstation.get("workstationName", None)] = score
            self.logger.debug("Scores: {}".format(scores))

        if len(scores) == 0:
            return None


        if max(scores) > 0:
            selected = max(scores, key=scores.get)
            self.logger.debug("Selected workstation: {}".format(selected))
            return selected
        else:
            return None


    def prepareForTransfer(self, job):
        return True

    def transfer(self, job):
        if self.pySchedServer.transferJob(job):
            return True
        else:
            return False

    def compilingCompleted(self, job):
        self.logger.info("Compiling completed.")
        job.stateId = JobState.lookup("COMPILED")
        self.pySchedServer.updateDatabaseEntry(job)
        self.transferJob(job)

    def compilingFailed(self, job):
        job.stateId = JobState.lookup("COMPILER_ERROR")
        self.pySchedServer.updateDatabaseEntry(job)
        self.logger.error("Failed to compile job {}".format(job.jobId))

