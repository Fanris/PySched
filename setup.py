#!/usr/bin/env python

from setuptools import setup

setup(name='PySched',      
      version='1.0',
      description='PySched - A Python network scheduler.',
      author='Martin Predki',
      author_email='martin.predki@rub.de',
      url='https://github.com/Fanris/PySched',
      license='LGPL'
      packages=[
            'PySched',
            'PySched.Common',
            'PySched.Common.Communication',
            'PySched.Common.IO',
            'PySched.Common.Interfaces',
            'PySched.Common.Interfaces.DatabaseInterface',
            'PySched.Common.Interfaces.JobRunnerInterface',
            'PySched.Common.Interfaces.Network',
            'PySched.Common.Interfaces.SchedulerInterface',
            'PySched.Common.Interfaces.WIMInterface',
            'PySched.PySchedClient',
            'PySched.PySchedClient.DatabaseManagement',
            'PySched.PySchedClient.JobRunner',
            'PySched.PySchedClient.NetworkManagement.',
            'PySched.PySchedClient.NetworkManagement.SSH',
            'PySched.PySchedClient.NetworkManagement.TcpClient',
            'PySched.PySchedClient.NetworkManagement.UdpClient',
            'PySched.PySchedClient.WorkstationInformationManager',
            'PySched.PySchedServer',
            'PySched.PySchedServer.DatabaseManagement',
            'PySched.PySchedServer.NetworkManagement',
            'PySched.PySchedServer.NetworkManagement.TcpServer',
            'PySched.PySchedServer.NetworkManagement.UdpServer',
            'PySched.PySchedServer.Scheduler',
            'PySched.PySchedServer.Scheduler.Compiler'
      ],
      install_requires=['SQLalchemy',
                        'twisted',
                        'psutil',
                        'paramiko',],
      scripts=[
            'PySched/PySchedClient/PySchedClient.sh',
            'PySched/PySchedServer/PySchedServer.sh'],
)
