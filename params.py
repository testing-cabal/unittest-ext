import unittest

class Paramaterizer(type):
    def __new__(meta, class_name, bases, attrs):
        try:
            params = attrs['params']
        except KeyError:
            raise Exception('Parameterized tests must provide a params class attribute')
            
        for name, scenarios in params.items():
            if name not in attrs:
                raise Exception('Test class %s does not have a method: %r' % 
                                (class_name, name))
            
            for index, args in enumerate(scenarios):
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
        
class TestCaseWithParams(unittest.TestCase):
    __metaclass__ = Paramaterizer
    params = {}
    
class Test(TestCaseWithParams):
    params = {
        'assertEqualWithParams': [dict(a=1, b=2), dict(a=3, b=3),
                                  dict(a=5, b=4)],
        'assertZeroDivisionWithParams':[dict(a=1, b=0), dict(a=3, b=2)]
        
        }
    
    def assertEqualWithParams(self, a, b):
        self.assertEqual(a, b)

    def assertZeroDivisionWithParams(self, a, b):
        self.assertRaises(ZeroDivisionError, lambda: a/b)

if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
    