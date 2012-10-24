from django.conf import settings
from tests.settings import TEST_SETTINGS

settings.configure(**TEST_SETTINGS)

def runtests():
    from django.test.simple import DjangoTestSuiteRunner
    import sys

    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(['tests'])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
