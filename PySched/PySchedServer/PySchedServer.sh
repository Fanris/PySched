#!/usr/bin/env python

from subprocess import call

import os
import sys
import argparse

def main(args=None):
    from PySched import PySchedServer
    #===============================================================================
    # Main Server Program
    #===============================================================================
    parser = argparse.ArgumentParser(description="PySched UI")
    parser.add_argument("-v", '--verbose', action='store_true', help="Be more verbose")
    parser.add_argument("-q", '--quiet', action='store_true', help="Be quiet.")
    parser.add_argument("-d", '--debug', action='store_true', help="Debug mode")
    parser.add_argument("-m", '--multicast', help="Use non standard multicast group")
    parser.add_argument("workingDir", help="Sets the directory for job storage and execution")

    if not args:
        args = parser.parse_args()
    else:
        print "Reloading Modules"
        reload(PySchedServer)
        res = None

    res = PySchedServer.PySchedServer(args.workingDir, args)
    if res.runUpdate:
        if update(PySchedServer.__file__, args):            
            try:
                os.execl(sys.argv[0], *sys.argv)
            except Exception e:
                res.logger.error(e)

def update(res, installPath, args):
    res.logger.info("PySchedServer terminated.")
    res.logger.info("Starting update...")

    installPath = installPath.replace("pysched/PySched/PySchedServer/__init__.py", "")
    installPath = installPath.replace("pysched/PySched/PySchedServer/__init__.pyc", "")
    res.logger.info("Install path = {}".format(installPath))
    res.logger.info("Downloading new version...")

    ret = call([
        "pip", 
        "install", 
        "--user", 
        "--src={}".format(installPath), 
        "-e", 
        "git://github.com/Fanris/PySched#egg=PySched"])

    if ret == 0:
        res.logger.info("Download / Install complete!")
        return True 
    else:
        res.logger.info("Failed to download / install PySchedServer!")

if __name__ == '__main__':
    main()
