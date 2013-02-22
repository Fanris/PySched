# -*- coding: utf-8 -*-
'''
Created on 2012-09-24 15:00
@summary: Protocol class for server side compile processes
@author: Martin Predki
'''


from twisted.internet import protocol

import os.path

class CompilerProcessProtocol(protocol.ProcessProtocol):
    '''
    @summary: Protocol class for job processes
    '''

    def __init__(self, job, jobDir, compiler):
        self.job = job
        self.jobDir = jobDir
        self.compiler = compiler

        self.stdOutput = open(os.path.join(self.jobDir, "logs", "compilerOutput"), "w+")
        self.errOutput = open(os.path.join(self.jobDir, "logs", "compilerError"), "w+")

    def connectionMade(self):
        self.stdOutput.write("Begin with compile process...")

    def outReceived(self, data):
        self.stdOutput.write(data)

    def errReceived(self, data):
        self.errOutput.write(data)

    def processEnded(self, status):
        self.stdOutput.close()
        self.errOutput.close()

        if status.value.exitCode == 0:
            self.compiler.compilingCompleted(self.job)
        else:
            self.compiler.compilingFailed(self.job)

    def kill(self):
        self.transport.signalProcess('KILL')
