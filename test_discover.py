import unittest

def f():
    foo
f()
class Test(unittest.TestCase):
    def testFail(self):
        self.fail()


if __name__ == '__main__':
    unittest.main()
