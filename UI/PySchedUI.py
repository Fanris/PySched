#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-01-15 13:23
@summary:
@author: predki
'''

from PySchedUI import PySchedUI
import argparse

def main():
    parser = argparse.ArgumentParser(description="PySched UI")
    parser.add_argument("-v", '--verbose', action='store_true', help="Be more verbose")
    parser.add_argument("-d", '--debug', action='store_true', help="Debug Mode")
    parser.add_argument("-u", '--user', help="The username to use for this session")
    parser.add_argument("-k", '--key', help="The private key file for the ssh tunnel.")
    parser.add_argument("-q", '--quiet', action='store_true', help="Be quiet")
    subparsers = parser.add_subparsers(title="Subcommands", help="sub-command help")

    ui = subparsers.add_parser('ui', help="Shows the user interface.")
    ui.set_defaults(func=startUI)

    getJobsParser = subparsers.add_parser('get_Jobs', help="Returns a list with all jobs.")
    getJobsParser.add_argument('userId', help="Username / Id for which the jobs should be retrieved")
    getJobsParser.add_argument('--showAll', action='store_true', help="Shows all jobs including archived")
    #getJobsParser.set_defaults(func=getJobs)

    addJobParser = subparsers.add_parser('add_Job', help="Adds a new Job to the scheduler.")
    addJobParser.add_argument('jobName', help="The name of the Job")
    addJobParser.add_argument('solver', help="The id of the solver to use")
    addJobParser.add_argument('user', help="The Username or id")
    addJobParser.add_argument('parameter', help="Additional parameter for this job", default="", nargs=argparse.REMAINDER)
    #addJobParser.set_defaults(func=addJob)

    abortJobParser = subparsers.add_parser('abort_Job', help="Aborts an Job")
    abortJobParser.add_argument('id', help="The id of the job")
    abortJobParser.add_argument('user', help="Id / name of the current")
    #abortJobParser.set_defaults(func=abortJob)

    archiveJobParser = subparsers.add_parser('archive_Job', help="Archives an Job")
    archiveJobParser.add_argument('id', help="The id of the job")
    archiveJobParser.add_argument('user', help="Id / name of the current")
    #archiveJobParser.set_defaults(func=archiveJob)

    getResultsParser = subparsers.add_parser('get_Results', help="Copies the results of an Job to the client.")
    getResultsParser.add_argument('path', help="The path where the Results should be saved.")
    getResultsParser.add_argument('id', help="The id of the job")
    getResultsParser.add_argument('user', help="Id / name of the current")
    #getResultsParser.set_defaults(func=results)

    scheduleParser = subparsers.add_parser('schedule', help="Forces the server to Schedule all Queued Jobs ## DEBUG-PURPOSE ##")
    #scheduleParser.set_defaults(func=schedule)


    args = parser.parse_args()
    args.func(args)

def startUI(args):
    PySchedUI(args)


if __name__ == "__main__":
    main()
