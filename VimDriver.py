
import re
import os
import time
from ave.util.Log import Log
from ave.util import SysUtil
from ave.util import StringUtil
from ave.util import FileUtil

ScriptDir = os.path.dirname(os.path.realpath(__file__))

class VimDriver:
    def __init__(self, serverName):
        self._serverName = serverName.upper()
        self._proc = None

    EmptyVimRc = FileUtil.ChangeToForwardSlashes(os.path.join(ScriptDir, 'EmptyVimRc.vim'))

    def normal(self, val = '', remap = True):
        self.feedkeys('<esc>' + val, remap, addUndoEntry = True)

    def insert(self, val):
        self.normal("i" + val)

    @property
    def line(self):
      return self.evaluate("getline('.')")

    @property
    def lineNo(self):
      return int(self.evaluate("line('.')"))

    @property
    def columnNo(self):
      return int(self.evaluate("col('.')"))

    @property
    def isServerUp(self):
        output = SysUtil.getOutput('vim --serverlist')
        serverNames = [x.strip() for x in output.split('\n')]
        return self._serverName in serverNames

    def startVanilla(self):
        self.start(VimDriver.EmptyVimRc)

    def start(self, vimrc = None):
        assert not self._proc

        commandStr = 'gvim --servername %s' % (self._serverName)

        if vimrc:
            commandStr += " -u %s" % vimrc

        self._proc = SysUtil.execute(commandStr, expand = False)

        while not self.isServerUp:
            time.sleep(0.1)

        # Wait for an evaluate to succeed before returning
        # This seems to help in cases where large vimrc's take awhile to load
        self.mode

    def stop(self):
        self.command('qall!')

        if self._proc:
            self._proc.waitForResult()
            self._proc = None

    # Similar to _rawType except a bit more flexible since you can choose whether to remap or not
    def feedkeys(self, keys, remap = True, addUndoEntry = False):

        if addUndoEntry:
            self._addUndoEntry()

        rawText = r'call feedkeys("%s", "%s")' % (self._escapeFeedKeys(keys), 'm' if remap else 'n')
        self._rawCommand(rawText)

    def undo(self):
        self.command('undo')

    def redo(self):
        self.command('redo')

    def command(self, cmd):
        self._rawCommand(cmd)

    def evaluate(self, expr):
        return SysUtil.getOutput('vim --servername %s --remote-expr "%s"' % (self._serverName, self._escapeRawType(expr)), expand = False)

    def getRegister(self, reg):
        return self.evaluate("getreg('%s')" % reg)

    def clearBuffer(self):
        self.normal(r'gg"_dG', remap = False)

    @property
    def mode(self):
        return self.evaluate('mode(1)')

    def _escapeRawType(self, keys):
        return StringUtil.escape(keys, r'\\|"')

    def _escapeRawCommand(self, val):
        return re.sub(r'\<\b(\w+)\b\>', r'\<\1_<bs>>', val)

    def _escapeFeedKeys(self, val):
        val = val.replace('"', '\\"')
        return val

    def _addUndoEntry(self):
        self._rawCommand("set undolevels=%s" % self.evaluate("&ul"))

    # Executes the given key
    # eg: rawCommand(r'echo "hi"')
    def _rawCommand(self, keys):
        mode = self.mode

        prefix = ''
        suffix = ''

        if mode == 'n':
            prefix = ':'
        elif mode == 'i':
            prefix = '<c-o>:'
        elif mode == 'v' or mode == 'V':
            prefix = ':<c-w>'
            suffix = 'gv'
        else:
            prefix = '<esc>:'

        self._rawType("%s%s<cr>%s" % (prefix, self._escapeRawCommand(keys), suffix))

    # Just forwards the given keys directly to vim
    # Useful if you don't want to exit visual/insert mode
    def _rawType(self, keys):
        SysUtil.executeAndWait('vim --servername %s --remote-send "%s"' % (self._serverName, self._escapeRawType(keys)), expand = False)

