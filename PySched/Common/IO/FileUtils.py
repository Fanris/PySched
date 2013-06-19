# -*- coding: utf-8 -*-
'''
Created on 2012-12-04 11:40
@summary: Package for File in / output
@author: Martin Predki
'''

import hashlib
import os
import shutil

def expandPath(path):
    tmp = path
    tmp = os.path.expanduser(tmp)
    tmp = os.path.expandvars(tmp)
    return tmp

def createDirectory(path):
    '''
    @summary: Creates an directory at the given path
    @param path: Path to the directory
    '''
    path = expandPath(path)
    if not os.path.exists(os.path.normpath(path)):
        os.makedirs(os.path.normpath(path))

    return path

def createFile(path, filedata):
    '''
    @summary: Creates a file with the given data at the directory
    @param pathToFile: path to directory
    @param filename: The name of the File
    @result: Absolute path to the File
    '''
    path = expandPath(path)
    dirname = os.path.split(path)[0]

    if not os.path.exists(dirname):
        createDirectory(dirname)

    fileHandler = open(path, "w+")
    if filedata:
        fileHandler.write(filedata)
    fileHandler.close()

    return os.path.normpath(path)

def createOrAppendToFile(path, filedata):
    '''
    @summary: Creates a file with the given data at the directory
    @param pathToFile: path to directory
    @param filename: The name of the File
    @result: Absolute path to the File
    '''
    path = expandPath(path)

    if not os.path.exists(path):
        createFile(path, None)

    with open(os.path.normpath(path), "a") as fileHandler:
        if filedata:
            fileHandler.write(filedata)    

    return os.path.normpath(path)

def deleteFile(path):
    '''
    @summary: Deletes a file
    @param pathToFile: The file to delete
    @result:
    '''
    path = expandPath(path)
    try:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
    except:
        pass

def clearDirectory(path, deleteSubfolders=True):
    '''
    @summary: Deletes all files within the folder
    @param pathToDir: path to the folder
    @result:
    '''
    path = expandPath(path)
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            filepath = os.path.join(path, f)
            if deleteSubfolders or not os.path.isdir(filepath):
                deleteFile(filepath)

def copyFile(source, dest):
    '''
    @summary: Copies a file from from source to dest
    @param source: File to copy
    @param dest: Destination
    @result:
    '''
    try:
        source = expandPath(source)
        dest = expandPath(source)

        shutil.copy(source, dest)
    except:
        pass

def moveFile(source, dest):
    '''
    @summary: Copies a file from from source to dest
    @param source: File to copy
    @param dest: Destination
    @result:
    '''
    try:
        source = expandPath(source)
        dest = expandPath(source)

        shutil.move(source, dest)
    except:
        pass

def validateFileMD5(path, originalMD5):
    '''
    @summary: Checks the MD5-Hashsum an file against it's original hash
    @param pathToFile: File to check
    @param originalMD5: Original MD5-Hashsum
    @result: True if both Hashsums are equal
    '''
    path = expandPath(path)
    if getFileMD5Hashsum(path) == originalMD5:
        return True

    return False

def getFileMD5Hashsum(path):
    '''
    @summary: Computes the MD5-Hashsum of the given File
    @param pathToFile: Path to file
    @result: The MD5-Hashsum as String
    '''
    path = expandPath(path)
    md5_hash = hashlib.md5()
    for bytes in readBytesFromFile(path):
        md5_hash.update(bytes)

    return md5_hash.hexdigest()

def readBytesFromFile(path, chunk_size=1000):
    '''
    @summary: Reads the given File chunk-wise.
    @param pathToFile: Path to File
    @param chunk_size: Size of each chunk
    @result: Returns the next chunk of the File
    '''
    path = expandPath(path)
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)

            if chunk:
                yield chunk
            else:
                break

def getFileSize(path):
    '''
    @summary: Returns the file size in kb or None, if the file
    does not exists
    @param pathToFile: Path to file.
    @result:
    '''
    path = expandPath(path)
    if os.path.exists(path):
        return os.path.getsize(path) / 1024
    else:
        return None

def readFile(path):
    '''
    @summary: Reads a complete file
    @param pathToFile:
    @result: Returns a list with all lines
    '''
    path = expandPath(path)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.readlines()     

def readLinesFromFile(pathToFile, lineCount=0, rev=False):
    '''
    @summary: Reads lineCount lines from a file.
    @param pathToFile: Path to the file
    @param lineCount: Lines to read (0 = Whole file)
    @param rev: Read first lines (reversed=False) or last lines 
                    (reversed=True)
    @result: 
    '''
    f = readFile(pathToFile)
    print f
    if f:
        if lineCount <= 0:
            return f

        if rev:
            return f[-lineCount:]
        else:
            return f[:lineCount]

def getDirectoryStructure(pathToDir, subFolders=True):
    '''
    @summary: Returns all files within the given directory
    @param pathToDir: Path to the directory
    @param subFolders: Descent in every Subfolder
    @result: 
    '''
    files = []
    if os.path.isdir(pathToDir):
        fileList = os.listdir(pathToDir)

        for f in fileList:            
            fullPath = os.path.join(pathToDir, f)
            if os.path.isdir(fullPath):
                files.append(f + os.sep)

                if subFolders:
                    for sf in getDirectoryStructure(fullPath):
                        files.append(os.path.join(f, sf))
            else:
                files.append(f)

    return files
