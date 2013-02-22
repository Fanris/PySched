# -*- coding: utf-8 -*-
'''
Created on 2012-10-08 16:09
@summary: PySched User Script
@author: Martin Predki
'''

from UI import UI
from Network import Network
from Common import pack, deleteFile

import os
import logging

class PySchedUI(object):
    '''
    @summary: PySchedUI Class
    '''

    def __init__(self, args):
        '''
        @summary: Initializes the PySchedUI
        @result:
        '''
        self.initializeLogger(args)
        self.debug = args.debug
        self.username = args.user
        self.network = Network(self, args.debug, keyFile=args.key)
        self.ui = UI(self, args.debug, username=self.username)

        if self.network.openConnection():
            self.ui.showMainMenu()

    def addJob(self, username, jobName, jobDescr, pathToTemplate):
        '''
        @summary: Adds a job with a template
        @param username: the username
        @param template: the path to the template
        @result:
        '''
        template = self.parseTemplate(pathToTemplate)
        paths = list(template.get("paths", []))
        if "paths" in template:
            del template["paths"]

        self.logger.debug(paths)

        returnValue = self.network.sendCommand("addJob", username=username, jobName=jobName, jobDescription=jobDescr, **template)

        if returnValue.get("result", False):
            jobId = returnValue.get("jobId", None)

            if not jobId:
                return False

            path = pack("{}.tar".format(jobId), *paths)
            if path:
                returnValue = self.network.sendFile(path)
                deleteFile(path)

                if returnValue.get("result", False):
                    return True
                else:
                    return False

            return True
        else:
            return False


    def createUser(self, firstName, lastName, email):
        returnValue = self.network.sendCommand("createUser", firstName=firstName, lastName=lastName, email=email)
        return returnValue.get("result", False)

    def getJobs(self, userId, showAll):
        returnValue = self.network.sendCommand("getJobs", username=userId, showAll=showAll)
        return returnValue.get("jobs", None)

    def getCompiler(self):
        return self.network.sendCommand("getCompiler").get("compiler", None)

    def abortJob(self, username, jobId):
        returnValue = self.network.sendCommand("killJob", username=username, jobId=jobId)
        if returnValue.get("result", False):
            return False

        return True

    def checkJobs(self):
        self.network.sendCommand("checkJobs", waitForResponse=False)

    def archiveJob(self, jobId, username):
        self.network.sendCommand("archiveJob", waitForResponse=False, username=username, jobId=jobId)

    def forceSchedule(self):
        self.network.sendCommand("schedule", waitForResponse=False)

    def getResults(self, username, jobId, path):
        self.network.sendCommand("getResults", jobId=jobId, username=username)
        return self.network.getFile(path)

    def deleteJob(self, username, jobId):
        returnValue = self.network.sendCommand("deleteJob", waitForResponse=True, username=username, jobId=jobId)
        if returnValue.get("result", False):
            return True

        return False

    def parseTemplate(self, pathToTemplate):
        '''
        @summary: Parses a template and returns a dictionary containing all the specified values
        @param pathToTemplate: The path to the template
        @result:
        '''
        if not os.path.exists(pathToTemplate):
            self.logger.error("Path {} does not exists.".format(pathToTemplate))
            return False

        with open(pathToTemplate) as templateFile:
            template = {}
            currentSection = ""

            for line in templateFile:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue

                if line.startswith("["):
                    currentSection = line.strip("[]")
                    continue

                if not self.parse(line, currentSection, template):
                    self.logger.error("Error on parsing line: {}".format(line))
                    return False

        return template

    def parse(self, line, section, template):
        '''
        @summary: parses a line and adds its values to the template
        @param line: the line to parse
        @param section: the current section
        @param template: the template to store the values in
        @result:
        '''
        if section.upper() == "CONFIG":
            key, value = line.split("=")
            if value.strip().upper() == "TRUE":
                template[key.lower()] = True
            elif value.strip().upper() == "FALSE":
                template[key.lower()] = False
            else:
                self.logger.debug("Adding {}={} to template".format(key, value))
                # transform key to equal the datastructure
                splitted = key.split("_")
                newKey = splitted[0].lower()
                for s in splitted[1::]:
                    newKey += s
                template[newKey] = value

            return True

        if section.upper() == "PATH":
            paths = template.get("paths", [])
            if len(paths) == 0:
                self.logger.debug("Adding path {} to template".format(line))
                paths.append(line)
                template["paths"] = paths
                return True

            self.logger.debug("Adding path {} to template".format(line))
            paths.append(line)
            return True

        if section.upper() == "COMPILER":
            self.logger.debug("Adding compilerStr {} to template".format(line))
            template["compilerStr"] = line
            return True

        if section.upper() == "PROGRAMS":
            programs = template.get("reqPrograms", [])
            if len(programs) == 0:
                self.logger.debug("Adding program {} to template".format(line))
                programs.append(line)
                template["reqPrograms"] = programs
                return True

            self.logger.debug("Adding program {} to template".format(line))
            paths.append(line)
            return True

        if section.upper() == "EXECUTION":
            self.logger.debug("Adding executeStr {} to template".format(line))
            template["executeStr"] = line
            return True

        return False

    def initializeLogger(self, args):
        '''
        @summary: Initializes the logger
        @param workingDir:
        @param args:
        @result:
        '''
        self.logger = logging.getLogger("PySchedUI")
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
        formatter = logging.Formatter('[%(levelname)s]: %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)
