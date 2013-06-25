#!/usr/bin/env python

from subprocess import call

import argparse
import os
import sys

def main(args=None):
    from PySched import PySchedClient
    #===============================================================================
    # Main Client Program
    #===============================================================================
    parser = argparse.ArgumentParser(description="PySched UI")
    parser.add_argument("-v", '--verbose', action='store_true', help="Be more verbose")
    parser.add_argument("-q", '--quiet', action='store_true', help="Be quiet.")
    parser.add_argument("-d", '--debug', action='store_true', help="Debug mode")
    parser.add_argument("-k", '--key', help="Path to the server key")
    parser.add_argument("-m", '--multicast', help="Use non standard multicast group")
    parser.add_argument("workingDir", help="Sets the directory for job storage and execution")
    
    if not args:
        args = parser.parse_args()
    else:
        print "Reloading Modules"
        reload(PySchedClient)
        res = None

    res = PySchedClient.PySchedClient(args.workingDir, args)
    if res.runUpdate:
        if update(res, PySchedClient.__file__, args):            
            try:
                os.execl(sys.argv[0], *sys.argv)
            except Exception, e:
                res.logger.error(e)

def update(res, installPath, args):
    res.logger.info("PySchedClient terminated.")
    res.logger.info("Starting update...")

    if installPath.endswith(".py"):
        installPath = installPath.replace("pysched/PySched/PySchedClient/__init__.py", "")
    else:
        installPath = installPath.replace("pysched/PySched/PySchedClient/__init__.pyc", "")

    res.logger.info("Install path = {}".format(installPath))
    res.logger.info("Downloading new version...")
    os.chdir(installPath)
    with open(os.path.join(res.workingDir, "updateLog.log"), 'w') as f:
        ret = call([
            "pip", 
            "install", 
            "--user", 
            "--no-deps",
            "--src={}".format(installPath), 
            "-e", 
            "git://github.com/Fanris/PySched#egg=PySched"],
            stdout=f)

    if ret == 0:
        res.logger.info("Download / Install complete!")
        return True 
    else:
        res.logger.info("Failed to download / install PySchedClient!")

if __name__ == '__main__':
    main()
