#!/usr/bin/env python3

# Copyright (c) [2022] [plotr.ai]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Setup script for the c3po Slack app.

Also installs third-party dependencies.
"""
from setuptools import find_packages, setup

import os
import io

def read(file, package_root=os.path.abspath(os.path.dirname(__file__))):
    filename = os.path.join(package_root, file)
    with io.open(filename, encoding="utf-8") as read_file:
        return read_file.read()

def version(version_script, package_root=os.path.abspath(os.path.dirname(__file__))):
    version = {}
    with open(os.path.join(package_root, version_script)) as fp:
        exec(fp.read(), version)
    return version["__version__"]

install_requires = [
    'flask~=2.1.2',
    'gunicorn~=20.1.0',
    'requests~=2.27.1',
    'sqlalchemy~=1.4.36',
    'psycopg2-binary~=2.9.3',
    'APScheduler==3.9.1',
    'Werkzeug==2.1.2',
    'slack-sdk~=3.16.0'
]

tests_require = [
    'pytest!=4.5.*',
    'mock!=3.0.*',
    'pylint!=2.11.*'
]

extras = {
    'test': tests_require
}

setup(
    name='c3po',
    version=version("c3po/version.py"),
    description="Human cyborg relations. How might I serve you?",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url='https://github.com/stewartmoreland/c3po',
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3',
    install_requires=install_requires,
    setup_requires=[
        'pytest-runner',
        'flake8'
    ],
    tests_require=tests_require,
    extras_require=extras,
    entry_points={
        'console_scripts': [
            'c3po = c3po.main:main',
        ]
    }
)
