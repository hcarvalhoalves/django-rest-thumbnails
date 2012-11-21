import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'testsuite.test_settings'

def runtests(tests=None):
    from django.test.simple import DjangoTestSuiteRunner

    if tests is None:
        tests = ['testsuite']

    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(tests)
    sys.exit(failures)

if __name__ == '__main__':
    runtests(sys.argv[1:])
