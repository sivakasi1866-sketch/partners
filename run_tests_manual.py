import sys
import unittest

loader = unittest.TestLoader()
start_dir = 'backend/app/tests'
suite = loader.discover(start_dir, pattern='test_*.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if not result.wasSuccessful():
    sys.exit(1)
