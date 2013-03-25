# -*- coding: utf-8 -*-
'''
Created on 2012-12-17 14:05
@summary: This file should give an overview of the used dictionary keys for
data transfer. It may be updated by other implementations.
@author: Martin Predki
'''

dictionaryOverview = {
	# Global keys:
	"command": "The command",
	"message": "A message. Used for plain text communication or to add further informations to another command",

	# User Informations:
	"username":		"The username of an user.",
	"firstName": 	"The first name of an user.",
	"lastName": 	"The last name of an user.",
	"email": 		"The email-address of an user.",

	# Job Informations:
	# These informations should be available for all jobs.
	"jobId": 		"The global job id",
	"jobName": 		"The name of the job.",
	"jobDescription":	"A Job description.",
	"jobState": 	"The current state of the job.",
	"addedOn": 		"Datetime when the job was added.",
	"scheduledOn": 	"Datetime when the job was scheduled,",
	"startedOn": 	"Datetime when the job was started.",
	"finishedOn": 	"Datetime when the job was finished.",
	"jobParameter": "A List of parameters to be added to the job start.",

	# Additional Job Informations:
	"compiler":		"The compiler to use if the job needs compiling",
	"compilerTarget":	"The compiler target",
	"compilerParameter":	"Additional compiler flags",

	# Workstation Informations:
	# Workstations informations are based on the requirements of the
	# implemented scheduler. They may vary or be updated.
	"workstationName": "Machine name of the workstation.",
	"os":			"Operating System of the workstation.",
	"cpuCount":		"CPU count of the workstation.",
	"cpuLoad": 		"CPU load of the workstation.",
	"memory":		"Overall memory of the workstation.",
	"memoryLoad":	"Used memory.",
	"activeUsers":	"Count of active users on the workstation.",
	"machine": 		"Machine informations of the workstation"
}
