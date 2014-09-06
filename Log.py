
import sys
import os
from datetime import datetime

# ////////////// Types

class LogType:
    Debug = 1
    Info = 2,
    Good = 3,
    Warn = 4,
    Error = 5,
    Heading = 6,

# ////////////// Data

_currentHeading = ''
_outStream = sys.stdout
_headerStartTime = None
_errorOccurred = False
_useColors = True

# ////////////// Public Methods

def SetStream(strm):
    global _outStream
    _outStream = strm

def StartHeading(msg):

    EndHeading()

    _errorOccurred = False
    _headerStartTime = datetime.now()

    _currentHeading = msg
    _LogInternal(msg + "...", LogType.Heading)

def EndHeading(msg = None):

    if not _headerStartTime:
        return

    delta = datetime.now() - _headerStartTime

    message = ""

    if _errorOccurred:
        message = "   Failed"
    else:
        message = "   Done"

    message = message + " (Took " + _FormatTimeDelta(delta.total_seconds()) + ")"

    # Always print out headings to stdout even if using a different stream
    if sys.stdout != _outStream:
        _EnableColor(LogType.Error if _errorOccurred else LogType.Good)
        print message
        _ClearColor()
        sys.stdout.flush()

    _PrintLine(message)
    Flush()
    _headerStartTime = None

    _LogInternal(msg, LogType.Good)

def Good(msg):
    _LogInternal(msg, LogType.Good)

def Info(msg):
    _PrintLine(msg)
    Flush()

def Error(msg):

    if _headerStartTime:
        _errorOccurred = True

    _LogInternal(msg, LogType.Error)

def Flush():
    _outStream.flush()

def _Print(value):
    print 'yepasdf ' + _outStream
    _outStream.write(value)

def _PrintLine(value):
    _outStream.write(value + '\n')

def _PrintSeperator():
    _PrintLine("**************************")

# ////////////// Private Methods

def _LogInternal(msg, logType):

    _PrintSeperator()

    _PrintLine(msg)

    _PrintSeperator()
    Flush()

    if sys.stdout != _outStream:
        _EnableColor(logType)
        print msg
        _ClearColor()
        sys.stdout.flush()

def _GetColorCode(logType):
    if logType == LogType.Error:
        return 31

    if logType == LogType.Good:
        return 32

    return 0

def _EnableColor(logType):
    if _useColors:
        colorCode = _GetColorCode(logType)

        if colorCode != 0:
            print '\033[%dm' % colorCode,

def _ClearColor():
    if _useColors:
        # Not sure why we need both of these for things to work
        print '\033[0m',
        print '\033[1m',

def _FormatTimeDelta(seconds):

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

