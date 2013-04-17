# -*- coding: utf-8 -*-
'''
Created on 2012-09-24 15:00
@summary: Protocol class for client side processes
@author: Martin Predki
'''


from PySched.Common.IO.FileUtils import createDirectory

from twisted.internet import protocol

import os.path

class JobProcessProtocol(protocol.ProcessProtocol):
    '''
    @summary: Protocol class for job processes
    '''

    def __init__(self, jobId, jobDir, jobRunner):
        self.jobId = jobId
        self.jobDir = jobDir
        self.aborted = False
        self.jobRunner = jobRunner

        createDirectory(os.path.join(self.jobDir, "results"))

        stdOutPath = os.path.join(self.jobDir, "results", "processOutput")
        self.stdOut = open(stdOutPath, "w+")

        stdErrPath = os.path.join(self.jobDir, "results", "errOutput")
        self.stdErr = open(stdErrPath, "w+")

    def connectionMade(self):
        self.jobRunner.jobStarted(self.jobId)

    def outReceived(self, data):
        self.stdOut.write(data)

    def errReceived(self, data):
        self.stdErr.write(data)

    def processEnded(self, status):
        self.stdOut.close()
        self.stdErr.close()

        if not self.aborted:
            if status.value.exitCode == 0:
                self.jobRunner.jobCompleted(self.jobId)
            else:
                self.jobRunner.jobFailed(self.jobId)

    def kill(self):
        self.aborted = True
        self.outReceived("\n\n")
        self.outReceived("Process terminated by user.")
        self.errReceived("\n\n")
        self.errReceived("Process terminated by user.")
        self.transport.signalProcess('KILL')
        self.jobRunner.jobAborted(self.jobId)
