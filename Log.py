
import sys
import os
from datetime import datetime

class LogType:
    Debug = 1
    Info = 2,
    Good = 3,
    Warn = 4,
    Error = 5,
    Heading = 6,

class _Impl:
    def __init__(self):
        self._currentHeading = ''
        self._outStream = sys.stdout
        self._headerStartTime = None
        self._errorOccurred = False
        self._useColors = True

    # ////////////// Public Methods

    def setStream(self, strm):
        self._outStream = strm

    def startHeading(self, msg):

        self.endHeading()

        self._errorOccurred = False
        self._headerStartTime = datetime.now()

        self._currentHeading = msg
        self._log(msg + "...", LogType.Heading)

    def endHeading(self, msg = None):

        if not self._headerStartTime:
            return

        delta = datetime.now() - self._headerStartTime

        message = ""

        if self._errorOccurred:
            message = "   Failed"
        else:
            message = "   Done"

        message = message + " (Took " + self._formatTimeDelta(delta.total_seconds()) + ")"

        self._printLine(message)
        self.flush()
        self._headerStartTime = None

        if msg:
            self._log(msg, LogType.Good)

    def good(self, msg):
        self._log(msg, LogType.Good)

    def info(self, msg):
        self._printLine(msg)
        self.flush()

    def error(self, msg):

        if self._headerStartTime:
            self._errorOccurred = True

        self._log(msg, LogType.Error)

    def flush(self, ):
        self._outStream.flush()

    def _print(self, value):
        self._outStream.write(value)

    def _printLine(self, value):
        self._outStream.write(value + '\n')

    def _printSeperator(self, ):
        self._printLine("**************************")

    # ////////////// Private Methods

    def _log(self, msg, logType):

        self._printSeperator()

        self._printLine(msg)

        self._printSeperator()
        self.flush()

        if sys.stdout != self._outStream:
            self._enableColor(logType)
            print msg
            self._clearColor()
            sys.stdout.flush()

    def _getColorCode(self, logType):
        if logType == LogType.Error:
            return 31

        if logType == LogType.Good:
            return 32

        return 0

    def _enableColor(self, logType):
        if self._useColors:
            colorCode = self._getColorCode(logType)

            if colorCode != 0:
                print '\033[%dm' % colorCode,

    def _clearColor(self, ):
        if self._useColors:
            # Not sure why we need both of these for things to work
            print '\033[0m',
            print '\033[1m',

    def _formatTimeDelta(self, seconds):

        hours = seconds // 3600

        msg = ""

        if hours > 0:
            msg += str(hours) + " hours, "

        # remaining seconds
        seconds = seconds - (hours * 3600)
        # minutes
        minutes = seconds // 60

        if minutes > 0:
            msg += str(minutes) + " minutes, "

        # remaining seconds
        seconds = seconds - (minutes * 60)

        msg += "{:.1f}".format(seconds) + " seconds"

        return msg

# Expose singleton logger
Log = _Impl()
