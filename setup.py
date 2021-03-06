#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
    name='c3po',
    version='0.1.0',
    description="Human cyborg relations. How might I serve you?",
    url='https://github.com/stewartmoreland/c3po',
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3',
    install_requires=[
        'flask~=2.1.2',
        'gunicorn~=20.1.0',
        'requests~=2.27.1',
        'sqlalchemy~=1.4.36',
        'psycopg2-binary~=2.9.3',
        'APScheduler==3.9.1',
        'Werkzeug==2.1.2',
        'slack-sdk~=3.16.0'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest!=4.5.*',
        'mock!=3.0.*',
        'pylint!=2.11.*'
    ],
    entry_points={
        'console_scripts': [
            'c3po = c3po.main:main',
        ]
    }
)
