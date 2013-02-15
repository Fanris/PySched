import hashlib
import os
import tarfile


def getFileMD5Hashsum(pathToFile):
    '''
    @summary: Computes the MD5-Hashsum of the given File
    @param pathToFile: Path to file
    @result: The MD5-Hashsum as String
    '''
    md5_hash = hashlib.md5()
    for bytes in readBytesFromFile(pathToFile):
        md5_hash.update(bytes)

    return md5_hash.hexdigest()

def readBytesFromFile(pathToFile, chunk_size=1000):
    '''
    @summary: Reads the given File chunk-wise.
    @param pathToFile: Path to File
    @param chunk_size: Size of each chunk
    @result: Returns the next chunk of the File
    '''
    with open(pathToFile, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)

            if chunk:
                yield chunk
            else:
                break

def pack(outputPath, *args):
    '''
    @summary: Creates an uncompressed tar-File with all files specified in args.
    @param outputPath: Output Path for the TAR-Archiv
    @param firstFolderContentInRoot: A flag specifying if the content of folders given in args should
    be stored at the root folder of the archive. So the parent directory of the given folder is splitted.
    E.g. args = /foo/bar.txt is packed as bar.txt in the archive.
    @param *args: List of files to put into the archive
    @result:
    '''
    if len(args) == 0:
        return None

    tar = tarfile.open(outputPath, "w")
    for filename in args:
        if not os.path.exists(filename.strip("*")):
            print "Error on creating archive! File {} does not exist!".format(filename.strip("*"))
            return None

        if filename.endswith("*"):
            filename = filename.strip("*")
            if os.path.isdir(filename):
                files = os.listdir(filename)
                for secFilename in files:
                    arcName = secFilename
                    addToArchive(tar, os.path.join(filename, secFilename), arcName)
        else:
            arcName = os.path.split(filename)[1]
            addToArchive(tar, filename, arcName)

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
    print "packing {}".format(filename)
    if os.path.isdir(filename):
        files = os.listdir(filename)
        for f in files:
            addToArchive(tar, os.path.join(filename, f), os.path.join(arcName, os.path.split(f)[1]))

    else:
        tar.add(name=filename, arcname=arcName)

def createAsciiTable(*rows):
    '''
    @summary: Creates an ASCII table for output
    @param *rows: Rows to be printed. A Row is a list of Strings
    where each String is the content of one Column. First Row is used as Header
    @result: A String containing the table
    '''
    columnCount = len(rows[0])
    columnLength = {}
    table = []

    # determine Column max width
    for row in rows:
        i = 0
        for word in row:
            #Logger.Log("createAsciiTable", "word: {}".format(word))
            length = len(word)
            key = str(i)
            currentLength = columnLength.get(key, None)

            if not currentLength or currentLength < length:
                columnLength[key] = length
            i = i + 1

    # create table Header
    header = ""
    for i in range(0, columnCount):
        key = str(i)
        header += "| " + rows[0][i].center(columnLength[key]) + " "

    header = header.lstrip("|")
    underline = ""
    for char in header:
        if char == "|":
            underline += "+"
        else:
            underline += "-"

    table.append(header)
    table.append(underline)

    # create rows
    for i in range(1, len(rows)):
        line = ""
        for j in range(0, columnCount):
            key = str(j)
            line += "| " + rows[i][j].center(columnLength[key]) + " "

        line = line.lstrip("|")
        table.append(line)

    return table

def deleteFile(pathToFile):
    '''
    @summary: Deletes a file
    @param pathToFile: The file to delete
    @result:
    '''
    if os.path.exists(pathToFile):
        os.remove(pathToFile)
