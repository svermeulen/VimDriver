
import sys
import unittest

from vimcommander.VimCommander import VimCommander

class Tests1(unittest.TestCase):

    def test1(self):
        self.failUnless(False)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
