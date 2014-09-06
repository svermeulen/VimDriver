
from Logger import Logger
import sys
import os
import shlex
import subprocess
import distutils.core
from ProcessTimeout import WaitForProcessOrTimeout, ResultType
import datetime
import zipfile
import shutil
import argparse
from glob import glob

#####################
# Responsibilities:
# - Miscellaneous file-handling/path-related operations
# - Substituting a given list of params into the paths
# - Wrapper to execute arbitrary commands
#####################
class SystemHelper:
    def __init__(self, params, logger, timeout = 60 * 5):
        self.Params = params
        self.logger = logger
        self.timeout = timeout

    def ExpandVars(self, text):
        try:
            while "{" in text:
                text = text.format(**self.Params)
        except KeyError, e:
            raise Exception("Unable to find key %s in the list of known paths" % e)

        return text

    def ExecuteAndWait(self, commandStr, startDir = None):
        expandedStr = self.ExpandVars(commandStr)

        self.logger.Log("Executing '%s'" % expandedStr)

        # Convert command to argument list to avoid issues with escape characters, etc.
        # Based on an answer here: http://stackoverflow.com/questions/12081970/python-using-quotes-in-the-subprocess-popen
        vals = shlex.split(expandedStr)

        if startDir != None:
            startDir = self.ExpandVars(startDir)

        result = WaitForProcessOrTimeout(vals, self.timeout, self.logger.OutStream, startDir)

        if result == ResultType.Error:
            raise Exception("Command returned with error code while executing: %s" % expandedStr)

        if result == ResultType.TimedOut:
            raise Exception("Timed out while waiting for command: %s" % expandedStr)

        assert result == ResultType.Success

    def ExecuteAndReturnOutput(self, commandStr):
        vals = shlex.split(commandStr)
        return subprocess.check_output(vals).strip()

    def MakeMissingDirectoriesInPath(self, dirPath):
        try:
            os.makedirs(os.path.dirname(dirPath))
        except:
            pass

    def CopyFile(self, fromPath, toPath):
        toPath = self.ExpandVars(toPath)
        fromPath = self.ExpandVars(fromPath)

        self.MakeMissingDirectoriesInPath(toPath)
        shutil.copy2(fromPath, toPath)

    def DeleteDirectoryContents(self, dirPath):
        dirPath = self.ExpandVars(dirPath)

        if os.path.exists(dirPath):
            shutil.rmtree(dirPath)

    def DeleteEmptyDirectoriesUnder(self, dirPath):
        dirPath = self.ExpandVars(dirPath)

        if not os.path.isdir(dirPath):
            return 0

        files = os.listdir(dirPath)

        numDirsDeleted = 0

        for fileName in files:
            fullpath = os.path.join(dirPath, fileName)

            if os.path.isdir(fullpath):
                numDirsDeleted += self.DeleteEmptyDirectoriesUnder(fullpath)

        files = os.listdir(dirPath)

        if len(files) == 0:
            self.logger.Log("Removing empty folder '%s'" % dirPath)
            os.rmdir(dirPath)
            numDirsDeleted += 1

            metaFilePath = dirPath + "/../" + os.path.basename(dirPath) + ".meta"

            if os.path.isfile(metaFilePath):
                self.logger.Log("Removing meta file '%s'" % metaFilePath)
                os.remove(metaFilePath)

        return numDirsDeleted

    def FileExists(self, path):
        return os.path.isfile(self.ExpandVars(path))

    def DirectoryExists(self, dirPath):
        return os.path.exists(self.ExpandVars(dirPath))

    def CopyDirectory(self, fromPath, toPath):
        fromPath = self.ExpandVars(fromPath)
        toPath = self.ExpandVars(toPath)

        distutils.dir_util.copy_tree(fromPath, toPath)

    def OpenOutputFile(self, path):
        return open(self.ExpandVars(path), 'w')

    def OpenInputFile(self, path):
        return open(self.ExpandVars(path), 'r')

    def RemoveFile(self, fileName):
        os.remove(self.ExpandVars(fileName))

    def RemoveFileIfExists(self, fileName):
        try:
            os.remove(self.ExpandVars(fileName))
        except OSError:
            pass

    def RemoveByRegex(self, regex):

        count = 0
        for filePath in glob(regex):
           os.unlink(filePath)
           count += 1

        self.logger.Log("Removed %s files matching '%s'" % (count, regex))

    def MakeMissingDirectoriesInPath(self, dirPath):
        try:
            os.makedirs(os.path.dirname(dirPath))
        except:
            pass

if __name__ == '__main__':
    logger = Logger(sys.stdout, True, True)
    sysHelper = SystemHelper({}, logger, 3)
    sysHelper.ExecuteAndWait('ls')

