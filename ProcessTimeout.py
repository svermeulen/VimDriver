import subprocess
from subprocess import Popen, PIPE
import signal, os, threading, errno
import sys
from contextlib import contextmanager
import time
import shlex

#####################
# These classes can be used to trigger commands through Popen and force-kill them after a given timeout
#####################

class ResultType:
    Success = 1
    Error = 2
    TimedOut = 3

class KillProcessThread(object):

    def __init__(self, seconds, pid):
        self.pid = pid
        self.timeOutOccurred = False
        self.seconds = seconds
        self.cond = threading.Condition()
        self.cancelled = False
        self.thread = threading.Thread(target=self.Wait)

        # Setting daemon to true will kill the thread if the main
        # thread aborts (eg. user hitting ctrl+c)
        self.thread.daemon = True

    def Run(self):
        """Begin the timeout."""
        self.thread.start()

    def Wait(self):
        with self.cond:
            self.cond.wait(self.seconds)

            if not self.cancelled:
                self.ForceKill()

    def Cancel(self):
        """Cancel the timeout, if it hasn't yet occured."""
        with self.cond:
            self.cancelled = True
            self.cond.notify()
        self.thread.join()

    def ForceKill(self):
        self.timeOutOccurred = True
        try:
            commandVals = shlex.split("taskkill /f /pid %i" % self.pid)
            Popen(commandVals, stdout=PIPE, stderr=PIPE)
        except OSError,e:
            # If the process is already gone, ignore the error.
            if e.errno not in (errno.EPERM, errno. ESRCH):
                raise e

def WaitForProcessOrTimeout(commandVals, seconds, outStream, startDir = None):

    params = {}
    params['stderr'] = outStream
    params['stdout'] = outStream

    if startDir != None:
        params['cwd'] = startDir

    proc = Popen(commandVals, **params)

    timeout = KillProcessThread(seconds, proc.pid)
    timeout.Run()

    try:
        while proc.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt, e:
        timeout.ForceKill()
        raise e

    timeout.Cancel()

    if timeout.timeOutOccurred:
        return ResultType.TimedOut

    resultCode = proc.wait()

    if resultCode != 0:
        return ResultType.Error

    return ResultType.Success

if __name__ == '__main__':
    print "Running test with 'sleep 3'"

    result = WaitForProcessOrTimeout(["sleep","1"], 2, subprocess.STDOUT)

    print result

