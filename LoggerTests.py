
import Log
import unittest

class TestStream:
    def __init__(self):
        self.buffer = ''

    def write(self, msg):
        self.buffer += msg

    def flush(self):
        pass

class LogTests(unittest.TestCase):

    def setUp(self):
        self.strm = TestStream()
        Log.SetStream(self.strm)

    def test1(self):
        Log.Info('hi')
        self.failUnlessEqual(self.strm.buffer, 'hi\n')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
