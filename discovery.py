import os
import sys
from unittest import TextTestRunner, TestLoader
from fnmatch import fnmatch

 
def name_from_path(path, top_level_dir):
    path = os.path.splitext(os.path.normpath(path))[0]
    
    # we don't handle drive / volume names
    # start_dir / top_level_dir on separate drives is an error anyway
    name = os.path.relpath(path, top_level_dir).replace(os.path.sep, '.')
    return name

        
class DiscoveringLoader(TestLoader):
    
    _top_level_dir = None
    
    def loadTestsFromModule(self, module):
        tests = TestLoader.loadTestsFromModule(self, module)
        load_tests = getattr(module, 'load_tests', None)
        if load_tests is not None:
            tests = load_tests(self, tests, None)
        return tests
    
    def discover(self, start_dir, include_filter, top_level_dir=None):
        if top_level_dir is None and self._top_level_dir is not None:
            # make top_level_dir optional if called from load_tests in a package
            top_level_dir = self._top_level_dir
        elif top_level_dir is None:
            top_level_dir = start_dir
            
        top_level_dir = os.path.abspath(os.path.normpath(top_level_dir))
        start_dir = os.path.abspath(os.path.normpath(start_dir))
    
        if not top_level_dir in sys.path:
            sys.path.append(top_level_dir)
        self._top_level_dir = top_level_dir
        
        is_top_level = start_dir == top_level_dir
        
        if not is_top_level and '__init__.py' not in os.listdir(start_dir):
            # what about __init__.pyc or pyo - and should probably allow .PY 
            # (differently cased extension) which would be valid on Windoze
            raise ImportError('Start directory is not importable: %r' % start_dir)
        
        tests = list(self._find_tests(start_dir, include_filter, is_top_level))
        return self.suiteClass(tests)
    

    def _find_tests(self, start_dir, include_filter, is_top_level):
        paths = os.listdir(start_dir)
        
        for path in paths:
            full_path = os.path.join(start_dir, path)
            # what about __init__.pyc or pyo - and should probably allow .PY 
            # (differently cased extension) which would be valid on Windoze
            # we would need to avoid loading the same tests multiple times
            # from '.py', '.pyc' *and* '.pyo'
            if os.path.isfile(full_path) and full_path.endswith('.py'):
                if fnmatch(path, include_filter):
                    module = self._get_module(name_from_path(full_path, self._top_level_dir))
                    yield self.loadTestsFromModule(module)
                    
            elif os.path.isdir(full_path):
                # what about __init__.pyc or pyo - and should probably allow .PY 
                # (differently cased extension) which would be valid on Windoze
                if '__init__.py' not in os.listdir(full_path):
                    continue
                
                load_tests = None
                if fnmatch(path, include_filter):
                    package = self._get_module(name_from_path(full_path, self._top_level_dir))
                    load_tests = getattr(package, 'load_tests', None)
                
                if load_tests is None:
                    print 'Recursing into:', full_path
                    for test in self._find_tests(full_path, include_filter, False):
                        yield test
                else:
                    yield load_tests(self, tests, include_filter)
        
    def _get_module(self, name):
        __import__(name)
        return sys.modules[name]
        

def discover(start_dir='.', include_filter='test*', top_level_dir=None, **kwargs):
    loader = DiscoveringLoader()
    suite = loader.discover(start_dir, include_filter, top_level_dir)
    
    # need to return exit code here
    TextTestRunner(**kwargs).run(suite)

    
if __name__ == '__main__':
    discover(*sys.argv[1:])
    
# uses os.path.relpath so requires Python 2.6+
# command line usage 'needs work'...
# doesn't handle __path__ for test packages that extend themselves in odd ways
# all tests must be in valid packages and importable from the top level of the project
# recognises packages through an explicit '__init__.py' file - no allowance for .pyo, .pyc, .so, .pyd, .zip etc
# should use code from load_from_dir in:
# http://bazaar.launchpad.net/~bzr/bzr/trunk/annotate/head%3A/bzrlib/plugin.py
