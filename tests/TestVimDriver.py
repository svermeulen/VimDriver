
import time
import sys
import unittest
from ave.util.Log import Log
from vimdriver.VimDriver import VimDriver

Log.setMinLevel(Log.Levels.info)
#Log.setMinLevel(Log.Levels.debug)

class TestsStartAndStop(unittest.TestCase):

    def setUp(self):
        self.driver = VimDriver('TEST_START_AND_STOP')

    def testStartAndStop(self):
        self.driver.startVanilla()
        self.assertTrue(self.driver.isServerUp)
        time.sleep(1)
        self.assertTrue(self.driver.isServerUp)
        self.driver.stop()
        self.assertFalse(self.driver.isServerUp)

    def testSeveralConsecutiveStartAndStop(self):

        for i in range(0, 5):
            self.driver.startVanilla()
            self.driver.insert('hi')
            self.assertEqual(self.driver.currentLine, 'hi')
            self.driver.stop()

    def testClearBuffer(self):
        self.driver.startVanilla()
        self.driver.clearBuffer()
        self.driver.insert('hi')
        self.assertEqual(self.driver.currentLine, 'hi')
        self.driver.clearBuffer()
        self.assertEqual(self.driver.currentLine, '')
        self.driver.stop()

# Enabling this keeps it open and makes it easier to debug
UseExistingVim = False

class Tests1(unittest.TestCase):

    def setUp(self):
        self.driver = VimDriver('TEST_VIMDRIVER')

        if UseExistingVim and self.driver.isServerUp:
            self.driver.clearBuffer()
        else:
            self.driver.startVanilla()

    def tearDown(self):
        if not UseExistingVim:
            self.driver.stop()

    def testMode(self):
        time.sleep(1)
        self.driver.normal('')
        self.assertEqual(self.driver.mode, 'n')
        self.driver.normal('i')
        self.assertEqual(self.driver.mode, 'i')
        self.driver.normal('v')
        self.assertEqual(self.driver.mode, 'v')
        self.driver.normal(':')
        self.assertEqual(self.driver.mode, 'c')

    def testInsert(self):
        self.driver.insert('hi')
        self.assertEqual(self.driver.currentLine, 'hi')
        self.assertEqual(self.driver.currentLineNo, 1)
        self.driver.normal('^')
        self.assertEqual(self.driver.columnNo, 1)
        self.driver.normal('$')
        self.assertEqual(self.driver.columnNo, 2)

    def testQuotationMarks(self):
        self.driver.command('normal! i"hi"')
        self.assertEqual(self.driver.currentLine, r'"hi"')

        self.driver.command('let test="hi"')
        self.assertEqual(self.driver.evaluate("test"), r'hi')

    def testVimCharacters(self):
        self.driver.insert('first line<esc>')
        self.assertEqual(self.driver.currentLine, r'first line')
        self.driver.normal('A<cr>second line')
        self.driver.normal('othird line')
        self.assertEqual(self.driver.currentLine, r'third line')

    def testCommandChars(self):
        # Make sure lots of characters make it there and back in one piece
        self.checkCommandStr(' bob    ')
        self.checkCommandStr(r'some text ^ & * % $ # ) ')
        self.checkCommandStr(r'blah ( [ ] / > < . , ? : ; { }  - + = _ ` ~ | stuff')

        # Quotes and backslashes need to be escaped since they are inside the 'let test=[]'
        testValue = r'text with quote \" yep'
        self.driver.command(r'let test = "%s"' % testValue)
        test = self.driver.evaluate('test')
        self.assertEqual(test, r'text with quote " yep')

        testValue = r'text with backslash \\ yep'
        self.driver.command(r'let test = "%s"' % testValue)
        test = self.driver.evaluate('test')
        self.assertEqual(test, r'text with backslash \ yep')

    def checkCommandStr(self, testValue):
        self.driver.command(r'let test = "%s"' % testValue)
        test = self.driver.evaluate('test')
        self.assertEqual(test, testValue)

    def testUndo(self):
        self.driver.normal('ofirst<esc>')
        self.driver.normal('osecond<esc>')
        self.driver.normal('othird<esc>')

        self.assertEqual(self.driver.currentLine, 'third')
        self.driver.undo()
        self.assertEqual(self.driver.currentLine, 'second')
        self.driver.undo()
        self.assertEqual(self.driver.currentLine, 'first')
        self.driver.redo()
        self.driver.normal('j') # redo doesn't restore cursor pos
        self.assertEqual(self.driver.currentLine, 'second')
        self.driver.redo()
        self.driver.normal('j') # redo doesn't restore cursor pos
        self.assertEqual(self.driver.currentLine, 'third')

    def testMultipleInserts(self):
        # Allow continuing in the same insert session using feedkeys
        self.driver.insert('hi')
        self.driver.feedkeys(' there')
        self.assertEqual(self.driver.currentLine, 'hi there')

    def testVisualMode(self):
        self.driver.insert('the quick black<esc>0')
        self.driver.normal('ve')
        self.assertEqual(self.driver.mode, 'v')
        self.driver.feedkeys('y')
        self.assertEqual(self.driver.getRegister('"'), 'the')
        self.driver.normal('0wde')
        self.assertEqual(self.driver.getRegister('"'), 'quick')

        self.driver.normal('V')
        self.assertEqual(self.driver.mode, 'V')
        self.driver.feedkeys('"_d')
        self.assertEqual(self.driver.currentLine, '')
        self.assertEqual(self.driver.getRegister('"'), 'quick')

    def testCommandOutput(self):
        result = self.driver.command('echo "hi"')
        self.assertEqual(result, 'hi')

        self.driver.normal('itest first')
        self.driver.normal('otest second')
        self.driver.normal('otest third')

        result = self.driver.command('%s/test/jim/')
        self.assertEqual(result, '3 substitutions on 3 lines')

        self.assertEqual(self.driver.getLine(1), 'jim first')
        self.assertEqual(self.driver.getLine(2), 'jim second')
        self.assertEqual(self.driver.getLine(3), 'jim third')

    def testMisc(self):
        self.driver.normal('iblurg (jimbo)<cr><esc>')
        self.driver.normal('kf(xye')
        self.assertEqual(self.driver.getRegister('"'), 'jimbo')

if __name__ == '__main__':
    unittest.main()

