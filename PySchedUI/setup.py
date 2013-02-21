#!/usr/bin/env python

from setuptools import setup

setup(name='PySchedUI',
      version='1.0',
      description='PySchedUI - A Python command line user Interface for PySched.',
      author='Martin Predki',
      author_email='martin.predki@rub.de',
      url='https://github.com/Fanris/PySched',
      packages=[
            'PySchedUI',
            'PySchedUI.Network'],
      install_requires=['paramiko',],
      scripts=['PySchedUI/PySchedUI.sh'],
)
