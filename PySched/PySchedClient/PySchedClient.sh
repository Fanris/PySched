#!/usr/bin/env python

from PySched.PySchedClient import PySchedClient

import argparse

def main():
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
    args = parser.parse_args()

    res = PySchedClient(args.workingDir, args)
    print "PySchedClient terminated with {}".format(res)
    print "Install path: {}".format(PySchedClient.__file__)

if __name__ == '__main__':
    main()
