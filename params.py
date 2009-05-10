import unittest

class Paramaterizer(type):
    def __new__(meta, class_name, bases, attrs):
        try:
            params = attrs['params']
        except KeyError:
            raise Exception('Parameterized tests must provide a params class attribute')
            
        try:
            assertMethod = attrs['assertWithParams']
        except KeyError:
            raise Exception('Parameterized tests must provide an assertWithParams method')
            
        for index, args in enumerate(params):
            def test(self, args=args):
                self.assertWithParams(*args)
            test.__doc__ = """Test with args: %s""" % (args,)
            name = 'test_with_params_%s' % (index + 1)
            test.__name__ = name
            
            if name in attrs:
                raise Exception('Test class %s already has a method called: %s' % (name, class_name))
            attrs[name] = test
        
        return type.__new__(meta, class_name, bases, attrs)
        
class TestCaseWithParams(unittest.TestCase):
    __metaclass__ = Paramaterizer
    params = []
    def assertWithParams(self):
        pass
    
class Test(TestCaseWithParams):
    params = [(1, 1), (2, 3), (2, 2), (3, 5)]
    
    def assertWithParams(self, a, b):
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
    