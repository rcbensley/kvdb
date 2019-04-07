#!/usr/bin/env python

from setuptools import setup


setup(
    name='kvdb',
    version='3.2.1',
    url='https://github.com/rcbensley/kvdb',
    description=("Key-Value-Database is a toy abstraction layer"
                 " which uses MariaDB 10.3+ to utilise the JSON data type"
                 " and System Versioning to answer that now aging question,"
                 " why on earth are you using key-value stores"
                 " and object databases?"),
    packages=['kvdb'],
    install_requires=['pymysql', ],
    keywords='kvdb',
)
