# -*- coding: utf-8 -*-
'''
Created on 2013-01-14 15:25
@summary: An overview of the contents of a workstation dictionary delivered by the PySchedClient.
The contents of the dictionary may vary due to other implementations of the WIM (Workstation Information Manager)
on the client side. If content delivered by the WIM is changed, it is highly recommended to update this
overview.

@author: Martin Predki
'''

workstationDictionaryOverview = {
	# Vital. This entry must be provided for the PySchedServer.
	"workstationName": "The machine name of the workstation",

	# Static entries
	"os": "The operating system of the workstation",
	"machine": "The machine architecture of the workstation (x86, x64...)",
	"cpuCount": "Count of available cpus",
	"memory": "Maximal available memory",
	"programs": "A list of available programs at the workstation",
	"diskAvailable":"Disk size",

	# dynamic entrie
	"cpuLoad": "The current cpu load",
	"memoryLoad": "The current memory load",
	"activeUsers": "The count of currently signed in users at the workstation",
	"diskLoad":		"Used Disk space",
	"diskFree":		"Free Disk space",
	"acitveJobs":	"Active Job count",
}
