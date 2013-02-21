#!/usr/bin/env python

from setuptools import setup

setup(name='PySchedServer',
      version='1.0',
      description='PySchedServer - A Python network scheduling server.',
      author='Martin Predki',
      author_email='martin.predki@rub.de',
      url='https://github.com/Fanris/PySched',
      packages=['PySched',
      			'PySched.Common', 
      			'PySched.Common.Communication',
      			'PySched.Common.IO',
      			'PySched.Common.Interfaces',
      			'PySched.Common.Interfaces.DatabaseInterface',
      			'PySched.Common.Interfaces.Network',
      			'PySched.Common.Interfaces.SchedulerInterface',
      			'PySched.PySchedServer',
      			'PySched.PySchedServer.DatabaseManagement',
      			'PySched.PySchedServer.NetworkManagement',
      			'PySched.PySchedServer.NetworkManagement.TcpServer',
      			'PySched.PySchedServer.NetworkManagement.UdpServer',
      			'PySched.PySchedServer.Scheduler',
      			'PySched.PySchedServer.Scheduler.Compiler',],
      install_requires=['SQLalchemy',
      			'twisted',],
      scripts=['PySched/PySchedServer/PySchedServer.sh'],
      )
