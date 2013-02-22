# -*- coding: utf-8 -*-
'''
Created on 2012-09-17 14:51
@summary: Class for Tar processing

@author: Martin Predki
'''

import tarfile
import os

def pack(outputPath, *args):
    '''
    @summary: Creates an uncompressed tar-File with all files specified in args.
    @param outputPath: Output Path for the TAR-Archiv
    @param *args: List of files to put into the archive
    @result:
    '''

    tar = tarfile.open(outputPath, "w")
    for filename in args:
        arcName = os.path.split(filename)[1]
        addToArchive(tar, filename, arcName)

    tar.close()
    return outputPath

def packFolder(outputPath, folder):
    '''
    @summary: Creates an uncompressed tar-File with all files in the specified folder.
    @param outputPath: Output Path for the TAR-Archiv
    @param *args: List of files to put into the archive
    @result:
    '''

    tar = tarfile.open(outputPath, "w")
    files = os.listdir(folder)
    for filename in files:
        arcName = filename
        addToArchive(tar, os.path.join(folder, filename), arcName)

    tar.close()
    return outputPath

def addToArchive(tar, filename, arcName):
    '''
    @summary: Recursive function.
    Adds a file or directory to an tar archive
    @param tar: an tar object to add the file to
    @param filename: the filename
    @param arcName: the filename within the archive
    '''

    if os.path.isdir(filename):
        files = os.listdir(filename)
        for f in files:
            addToArchive(tar, os.path.join(filename, f), os.path.join(arcName, os.path.split(f)[1]))

    else:
        tar.add(name=filename, arcname=arcName)

def unpack(filename, path=None):
    '''
    @summary: Unpacks the tar-Arhciv to the given folder.
    @param filename: Path to the Archiv
    @param path: Path to extract to. If none is given, extract
    the Archive within its current folder.
    @result:
    '''
    tar = tarfile.open(filename)

    if path:
        tar.extractall(path)
    else:
        tar.extractall(os.path.split(filename)[0])

    tar.close()

