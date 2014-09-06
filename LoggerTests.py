
from Log import Log
import sys
import unittest

class TestStream:
    def __init__(self):
        self.buffer = ''

    def write(self, msg):
        self.buffer += msg

    def flush(self):
        pass

class LogTests2(unittest.TestCase):
    def setUp(self):
        Log.setStream(sys.stdout)

    def test1(self):
        Log.startHeading('stuff')
        Log.info('hi')
        Log.endHeading()

class LogTests1(unittest.TestCase):

    def setUp(self):
        self.strm = TestStream()
        Log.setStream(self.strm)

    def test1(self):
        Log.info('hi')
        self.failUnlessEqual(self.strm.buffer, 'hi\n')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
