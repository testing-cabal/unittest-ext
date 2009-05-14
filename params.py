import unittest
from types import FunctionType

class Paramaterizer(type):
    def __new__(meta, class_name, bases, attrs):
        
        for name, item in attrs.items():
            if not isinstance(item, FunctionType):
                continue
            
            params = getattr(item, 'params', None)
            if params is None:
                continue
            
            for index, args in enumerate(params):
                def test(self, args=args, name=name):
                    assertMethod = getattr(self, name)
                    assertMethod(**args)
                test.__doc__ = """%s with args: %s""" % (name, args)
                test_name = 'test_%s_%s' % (name, index + 1)
                test.__name__ = test_name
                
                if test_name in attrs:
                    raise Exception('Test class %s already has a method called: %s' % 
                                    (class_name, test_name))
                attrs[test_name] = test
        
        return type.__new__(meta, class_name, bases, attrs)
        
def with_params(params):
    def decorate(func):
        func.params = params
        return func
    return decorate

class TestCaseWithParams(unittest.TestCase):
    __metaclass__ = Paramaterizer
    
class Test(TestCaseWithParams):
    
    @with_params([dict(a=1, b=2), dict(a=3, b=3), dict(a=5, b=4)])
    def assertEqualWithParams(self, a, b):
        self.assertEqual(a, b)

    @with_params([dict(a=1, b=0), dict(a=3, b=2)])
    def assertZeroDivisionWithParams(self, a, b):
        self.assertRaises(ZeroDivisionError, lambda: a/b)

if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
    