# -*- coding: utf-8 -*-
'''
Created on 2013-01-15 11:57
@summary:
@author: Martin Predki
'''

from Common import createAsciiTable

import os

class UI(object):
    '''
    @summary: UI class for the PySchedUI.
    '''

    def __init__(self, pySchedUI, debug=False, username=None):
        '''
        @summary: Initializes the UI
        @param pySchedUI: a reference to the main class
        @result:
        '''
        self.pySchedUI = pySchedUI
        self.debug = debug
        self.stop = False
        self.username = username
        self.functionList = [
            {"display": "Schedule a new Job with the cool new PySched Template", "function": self.showAddJobTemplateUI},
            {"display": "Show my Jobs", "function": self.showGetJobsUI},
            {"display": "Abort a Job", "function": self.showAbortJobUI},
            {"display": "Delete a Job", "function": self.showDeleteJobUI},
            #{"display": "Archive a Job", "function": self.archiveJob},
            {"display": "Get Job results", "function": self.showGetResultsUI},
            {"display": "Create / Edit an user", "function": self.showCreateUserUI},
            {"display": "Force scheduling (DEBUG)", "function": self.pySchedUI.forceSchedule},
            {"display": "Checking Jobs (DEBUG)", "function": self.pySchedUI.checkJobs},
            #{"display": "Get workstations (DEBUG)", "function": self.getWorkstations},
            {"display": "Nothing", "function": self.close}
        ]

        print "Welcome to PySched - A python network scheduler."
        print

    # UI Functions.
    # ======================================================
    def showMainMenu(self):
        while not self.stop:
            print
            print "Functions:"
            print "================================================"

            for functionIndex in range(0, len(self.functionList)):
                print "{index}: {display}".format(index=functionIndex + 1, display=self.functionList[functionIndex]["display"])
            print

            selected = raw_input("What do you want to do? ")

            try:
                selected = int(selected)
            except ValueError:
                selected = None

            if selected:
                function = None
                function = self.functionList[selected - 1]["function"]
                function()

    def showAddJobTemplateUI(self):
        '''
        @summary: Shows the add Job dialog with template supoort
        @result:
        '''
        inp = {}
        print
        print "Adding a new Job..."
        print "================================================"
        inp["Username"] = self.askForUsername()
        inp["Jobname"] = raw_input("Please enter a job name: ")
        inp["Description"] = raw_input("(Optional) A short description of the job: ")
        inp["template"] = os.path.normpath(raw_input("Please enter the path to the PySched-Config file: "))

        if self.showValidatingInput(inp):
            if self.pySchedUI.addJob(
                inp.get("Username", None),
                inp.get("Jobname", ""),
                inp.get("Description", ""),
                inp.get("template", None)):
                self.showJobTable(inp.get("Username", None), False)


    def showAddJobUI(self):
        '''
        @summary: Shows the add Job dialog.
        @param args:
        @result:
        '''
        inp = {}

        print
        print "Adding a new Job..."
        print "================================================"
        inp["Username"] = self.askForUsername()
        inp["Jobname"] = raw_input("Please enter a job name: ")
        inp["Description"] = raw_input("(Optional) A short description of the job: ")
        needToCompile = self.showYesNo("Does the program needs to be compiled or parsed? (y/n): ")

        if needToCompile:
            inp["Compiler"] = self.showSelectCompilerUI()
            inp["Target"] = raw_input("Please enter the compiler target: ")
            inp["Source"] = raw_input("Please enter the path to the sources (if the path points to a directory, the whole directory will be send to the server): ")
            inp["Compiler Parameter"] = raw_input("(Optional) Please enter any additional parameter which are passed to the chosen compiler (as a space seperated list): ")
        else:
            inp["Solver"] = os.path.normpath(raw_input("Please enter the path to the program or script: "))
            inp["Target"] = os.path.split(inp.get("Solver", ""))[1]

        inp["Inputfiles"] = []
        while True:
            inputfile = raw_input("Please enter the path to any external Inputfile or nothing if none is needed: ")
            if inputfile == "":
                break
            else:
                inp.get("Inputfiles", []).append(os.path.normpath(inputfile))

        inp["Job Parameter"] = raw_input("(Optional) Please enter any additional parameter that should be passed (as a space separated list): ")

        if self.showValidatingInput(inp):
            if self.pySchedUI.addJob(inp.get("Username", None),
                    inp.get("Jobname", ""),
                    inp.get("Description", ""),
                    inp.get("Compiler", {}),
                    inp.get("Target", ""),
                    inp.get("Compiler Parameter", ""),
                    inp.get("Inputfiles", []),
                    inp.get("Job Parameter", ""),
                    inp.get("Source", "") or inp.get("Solver", "")):
                print "Job added successful."
            else:
                print "Failed to add Job."


    def showSelectCompilerUI(self):
        compiler = self.pySchedUI.getCompiler()

        print
        print "Selecting Compiler or Parser..."
        print "================================================"
        for index in range(0, len(compiler)):
            print "{index}: {compilerName} - {descr}".format(index=index + 1, compilerName=compiler[index].get("compilerName", ""),
                descr=compiler[index].get("compilerDescription", ""))
        print
        selected = int(raw_input("Please select a compiler / parser: "))
        return compiler[selected - 1]

    def showCreateUserUI(self):
        '''
        @summary: Shows the create new user dialog.
        @param args:
        @result:
        '''
        inp = {}
        print
        print "Creating an new User..."
        print "================================================"
        inp["Email"] = raw_input("Please enter your email address: ")
        inp["First Name"] = raw_input("Please enter your first name (Optional): ")
        inp["Last Name"] = raw_input("Please enter your last name (Optional): ")

        if self.showValidatingInput(inp):
            if self.pySchedUI.createUser(
                inp.get("First Name", ""),
                inp.get("Last Name", ""),
                inp.get("Email", "")):
                print "User {} created.".format(inp.get("Email", None))
            else:
                print "Failed to create user."

    def showGetJobsUI(self):
        inp = {}
        print
        print "Getting job informations..."
        print "================================================"
        inp["username"] = self.askForUsername()
        inp["showAll"] = self.showYesNo("Show all jobs (inculding archived) (y/n)? ")

        self.showJobTable(
            inp.get("username", ""),
            inp.get("showAll", False))

    def showAbortJobUI(self):
        inp = {}
        print
        print "Aborting Job..."
        print "================================================"
        print
        inp["username"] = self.askForUsername()
        self.showJobTable(inp.get("username", ""), False)
        print
        inp["jobId"] = raw_input("Please enter the job id: ")
        if self.pySchedUI.abortJob(
            inp.get("username", ""),
            inp.get("jobId", None)):
            print "Job {} aborted.".format(inp.get("jobId", None))
        else:
            print "Could not abort the job."

    def showDeleteJobUI(self):
        inp = {}
        print
        print "Deleting Job..."
        print "================================================"
        print
        inp["username"] = self.askForUsername()
        self.showJobTable(inp.get("username", None), True)
        inp["jobId"] = raw_input("Please enter the job id: ")
        if self.showYesNo("Are you sure that you want to delete job {}?".format(inp.get("jobId", None))):
            if self.pySchedUI.deleteJob(
                inp.get("username", ""),
                inp.get("jobId", None)):
                print "Job deleted."
            else:
                print "Could not delete Job!"


    def showGetResultsUI(self):
        inp = {}
        print
        print "Getting Job results..."
        print "================================================"
        print
        inp["username"] = self.askForUsername()
        self.showJobTable(inp.get("username", None), True)
        inp["jobId"] = raw_input("Please enter the job id: ")
        inp["path"] = raw_input("Please select a path where the results should be stored: ")
        if self.pySchedUI.getResults(
            inp.get("username", ""),
            inp.get("jobId", None),
            inp.get("path")):
            print "Results stored in {}".format(inp.get("path", None))
        else:
            print "Could not retrieve the results of job {}".format(inp.get("jobId", None))

    def askForUsername(self):
        if self.username:
            print "Username: {}".format(self.username)
            return self.username
        else:
            return raw_input("Please enter your username: ")

    def showValidatingInput(self, inp):
        print
        print "Validating input..."
        print "================================================"
        print
        for k, v in inp.iteritems():
            print "{key}: \t\t{value}".format(key=k, value=v)

        return self.showYesNo("Are these values correct? (y / n): ")

    def showYesNo(self, message):
        answer = raw_input(message)
        if answer.lower() == "y":
            return True
        else:
            return False

    def showJobTable(self, username, showAll):
        jobs = self.pySchedUI.getJobs(
            username,
            showAll)

        rows = []
        header = ["ID", "Name", "State", "Added", "Started", "Ended", "Workstation", "Archived"]
        rows.append(header)

        if jobs:
            for job in jobs:
                rows.append([str(job.get("jobId", None)), job.get("jobName", None), job.get("stateId", None), str(job.get("added", None)), \
                    str(job.get("started", None)), str(job.get("finished", None)), str(job.get("workstation", None)), str(job.get("archived", None))])

        table = createAsciiTable(*rows)

        asciiTable = ""
        for row in table:
            asciiTable += row + '\r\n'

        print
        print asciiTable

    def close(self):
        self.stop = True
