#!/usr/bin/env python
from setuptools import setup
from setuptools.command.test import test


def readfile(fname):
    with open(fname) as fd:
        return u'\n'.join(fd.readlines())


class TestCommand(test):
    def run(self):
        from runtests import runtests
        runtests()


setup(
    name='django-rest-thumbnails',
    version='1.0b9',
    url='http://github.com/hcarvalhoalves/django-rest-thumbnails',
    description='Simple and scalable thumbnail generation via REST API',
    long_description=readfile('README.md'),
    author='Henrique Carvalho Alves',
    author_email='hcarvalhoalves@gmail.com',
    packages=[
        'restthumbnails',
        'restthumbnails.templatetags',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
    cmdclass={'test': TestCommand},
)
