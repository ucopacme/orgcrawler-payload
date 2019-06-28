#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_namespace_packages


VERSION = '0.0.0'
LONGDESC = '''
OrgCrawler Payloads
===================

A library of orgcrawler payload functions.

See full documentation at https://blle.blkje.com/index.html
'''


setup(
    name='orgcrawler.payload',
    version=VERSION,
    description='A library of orgcrawler payload functions',
    long_description=LONGDESC,
    long_description_content_type='text/x-rst',
    url='https://github.com/ucopacme/orgcrawler-payload',
    keywords='aws organizations boto3 orgcrawler',
    author='Ashley Gould - University of California Office of the President',
    author_email='agould@ucop.edu',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'botocore',
        'boto3',
        'orgcrawler',
    ],
    packages=find_namespace_packages(include=['orgcrawler.*']),
    zip_safe=False,

)
