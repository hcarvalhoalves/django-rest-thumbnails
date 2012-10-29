from django.conf import settings
from tests.settings import TEST_SETTINGS

import sys

settings.configure(**TEST_SETTINGS)

def runtests(tests):
    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(tests)
    sys.exit(failures)

if __name__ == '__main__':
    runtests(sys.argv[1:] or ['tests'])
