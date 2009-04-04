import os
import sys
from unittest import TestCase, TextTestRunner, TestLoader, TestSuite
from itertools import chain
from fnmatch import fnmatch


def find_files(start_dir, include_filter, exclude_filter, top_level):
    paths = os.listdir(start_dir)
    
    # what about __init__.pyc or pyo - and should probably allow .PY 
    # (differently cased extension) which would be valid on Windoze
    if not top_level and '__init__.py' not in paths:
        return
    
    for path in paths:
        full_path = os.path.join(start_dir, path)
        if os.path.isfile(full_path):
            if fnmatch(path, include_filter): 
                if exclude_filter is None or not fnmatch(path, exclude_filter):
                    yield full_path
        elif os.path.isdir(full_path):
            for entry in find_files(full_path, include_filter, exclude_filter, False):
                yield entry

                
def module_names_from_paths(test_paths, top_level_dir):
    names = []
    for path in test_paths:
        if not path.endswith('.py'):
            continue
        path = os.path.normpath(path)[:-3]
        
        # we don't handle drive / volume names
        name = os.path.relpath(path, top_level_dir).replace(os.path.sep, '.')
        yield name

        
class DiscoveringTestSuite(TestSuite):
    
    loaderClass = TestLoader
    
    def __init__(self, start_dir, include_filter, exclude_filter, is_top_level,
        top_level_dir):
        super(DiscoveringTestSuite, self).__init__()
        self._discovered = False
        self._start_dir = start_dir
        self._include_filter = include_filter
        self._exclude_filter = exclude_filter
        self._is_top_level = is_top_level
        self._top_level_dir = top_level_dir

    def discover(self):
        if self._discovered:
            return
        
        # Do test discovery. Note that this is typically invoked during
        # __iter__, so we have to yield the tests we find as well as mutating
        # self._tests to make them visible in e.g. repr(). We could use a
        # separate list to make things clearer.
        loader = self.loaderClass()
        test_paths = find_files(self._start_dir, self._include_filter,
            self._exclude_filter, self._is_top_level)
        
        # NB: loadTestsFromNames is not currently a generator. If it was test
        # running and discovery would progress in parallel.
        for test in loader.loadTestsFromNames(
            module_names_from_paths(test_paths, self._top_level_dir)):
            self.addTest(test)
            yield test

    def __iter__(self):
        return chain(super(DiscoveringTestSuite, self).__iter__(),
            self.discover())



def run(start_dir='.', include_filter='test*.py', exclude_filter=None, 
        top_level_dir=None, **kwargs):
    
    top_level_dir = os.path.abspath(top_level_dir or start_dir)
    if not top_level_dir in sys.path:
        sys.path.append(top_level_dir)
    
    is_top_level = False
    if top_level_dir is None or (os.path.abspath(start_dir) == os.path.abspath(top_level_dir)):
        is_top_level = True
    
    suite = DiscoveringTestSuite(start_dir, include_filter, exclude_filter, is_top_level)
    
    # need to return exit code here
    TextTestRunner(**kwargs).run(suite)

    
if __name__ == '__main__':
    run(*sys.argv[1:])
    
# uses os.path.relpath so requires Python 2.6+
# command line usage 'needs work'...
# doesn't handle __path__ for test packages that extend themselves in odd ways
# all tests must be in valid packages and importable from the top level of the project
# recognises packages through an explicit '__init__.py' file - no allowance for .pyo or .pyc
# currently we ignore the package files themselves (the __init__.py) unless it happens to match
# the filter!
# filters for test names on the wish list
