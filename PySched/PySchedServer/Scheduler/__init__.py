# -*- coding: utf-8 -*-
'''
Created on 2012-12-05 11:59
@summary: Standard scheduler implementation.
@author: Martin Predki
'''

from PySched.Common.Interfaces.SchedulerInterface import SchedulerInterface
from PySched.Common.DataStructures import JobState
from Compiler import Compiler as CompilerClass

from twisted.internet.task import LoopingCall

from time import sleep
from collections import deque

import copy
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

        self.jobQueue = deque()
        self.schedulingLoop = LoopingCall(self.scheduleNext)

    def scheduleNext(self):
        '''
        @summary: Schedules the next job of the queue.
        @result: 
        '''
        self.logger.debug("Scheduling next Job...")
        try:
            jobId = self.jobQueue.popleft()
            job = self.pySchedServer.getJob(jobId)
            if job.stateId <= JobState.lookup("WAITING_FOR_WORKSTATION"):
                super(PyScheduler, self).scheduleJob(
                    self.pySchedServer.getWorkstations(),
                    job)
            elif job.stateId == JobState.lookup("COMPILED"):
                self.transfer(job)
        except IndexError:
            self.logger.debug("All jobs scheduled. Stopping scheduling Loop.")
            try: 
                self.schedulingLoop.stop()
            except:
                pass

    def scheduleJob(self, job, workstations=None):
        '''
        @summary:   Overrides the standard scheduleJob implementenation
                    to add scheduling queue. The Problem is: If too many
                    Jobs are added at once, the scheduling algorithm is
                    faster than the workstation information loop. Thus
                    the known state of the workstation by the scheduler
                    doesn't represent the actual state. Therefore some kind
                    of Queue is needed to add a wait time between the job
                    scheduling.
        @param workstations: List of available Workstations
        @param job: The job to schedule
        @result: 
        '''
        if not job.jobId in self.jobQueue:
            self.logger.debug("Added Job to queue.")
            if job.stateId == JobState.lookup("COMPILED"):
                self.jobQueue.appendleft(job.jobId)
            else:
                self.jobQueue.append(job.jobId)
            if not self.schedulingLoop.running:
                try: 
                    self.schedulingLoop.start(15, now=True)
                except:
                    pass

                return True        


    def checkJobPermission(self, job):
        return True

    def checkUserPermission(self, job):
        return True

    def compileJob(self, job):
        if job.compilerStr == None or job.compilerStr == "":
            self.logger.info("No compiler needed.")
            self.compilingCompleted(job)
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
        workstationList = copy.copy(workstations)

        for workstation in workstationList:
            self.logger.debug("Checking workstation {}".format(workstation))
            freeCpus = 0
            # First check the installed OS
            if not None and not workstation.get("os", "").lower() == job.reqOS.lower():
                self.pySchedServer.addToJobLog(job.jobId, 
                    "{} not appropriate: Wrong OS".
                    format(workstation.get("workstationName"), None))
                continue

            for load in workstation.get("cpuLoad", []):
            # Count free cpus. Threshold of a free cpu is 20% CPU-Load
                if load < 20:
                    freeCpus += 1

            # reserved Cpus
            reserved = workstation.get("reserved", 0)
            freeCpus -= reserved

            self.logger.debug("Free cpu count: {}".format(freeCpus))
            # when no cpu is free, this workstation should not
            # be considered any further
            if freeCpus == 0:
                self.pySchedServer.addToJobLog(
                    job.jobId,
                    "{} not appropriate: No free resources".format(
                    workstation.get("workstationName"), None))
                continue

            if freeCpus < job.minCpu:
                self.pySchedServer.addToJobLog(
                    job.jobId,
                    "{} not appropriate: not enough free CPUs".format(
                    workstation.get("workstationName"), None))
                continue

            # when the workstation has not the required amount of
            # memory, it should not be considered any further
            if job.minMemory > workstation.get("memory", 0) * 1024:
                self.pySchedServer.addToJobLog(
                    job.jobId,                    
                    "{} not appropriate: Not enough Memory".format(
                    workstation.get("workstationName"), None))
                continue

            # Check for programs
            reqProgramsAvailable = True
            for program in job.reqPrograms:
                if program == "":
                    continue
                    
                self.logger.debug("Check workstation for Program: '{}'.".format(program))
                if program in workstation.get("programs", []):
                    continue

                else:
                    self.logger.info("Requesting program '{}' from {}".format(
                            program,
                            workstation.get("workstationName", None))
                        )
                    self.pySchedServer.checkForPrograms(
                        workstation.get("workstationName", None),
                        [program]
                        )
                    sleep(2)
                    
                    if program in workstation.get("programs", []):
                        continue
                    else:
                        reqProgramsAvailable = False
                        self.pySchedServer.addToJobLog(
                            job.jobId,
                            "{} not appropriate: Program '{}' not available".format(
                            workstation.get("workstationName", None), program))
                        break

            if not reqProgramsAvailable:
                continue
                
            score = 0
            # Dont use machines with many programs that aren't
            # used by the job
            notReqProgramCount = len(workstation.get("programs", [])) - len(job.reqPrograms)
            score -= 500 * notReqProgramCount

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

        selected = max(scores, key=scores.get)
        self.logger.debug("Selected workstation: {}".format(selected))
        self.pySchedServer.addToJobLog(
            job.jobId,
            "Workstation {} ({}) selected.".
            format(selected, max(scores)))
        return selected

    def workstationSelected(self, job):
        self.pySchedServer.reserveCPU(job)

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
        self.scheduleJob(job)

    def compilingFailed(self, job):
        job.stateId = JobState.lookup("COMPILER_ERROR")
        self.pySchedServer.updateDatabaseEntry(job)
        self.logger.error("Failed to compile job {}".format(job.jobId))

