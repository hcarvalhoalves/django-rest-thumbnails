import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'testsuite.settings'

def runtests(tests=None):
    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=2)
    failures = test_runner.run_tests(tests or ['testsuite'])
    sys.exit(failures)

if __name__ == '__main__':
    runtests(sys.argv[1:])
