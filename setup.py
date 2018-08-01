# coding: utf-8

from __future__ import with_statement, print_function, absolute_import

from setuptools import setup, find_packages

import imp
version = imp.load_source('cek.version', 'cek/version.py')

description = 'Python Micro SDK for the Clova Extension Kit'
with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(
    name='clova-cek-sdk',
    version=version.version,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='LINE Corp.',
    author_email='dl_pypi@linecorp.com',
    url='https://github.com/line/clova-cek-sdk-python/',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=['cryptography'],
    extras_require={'docs': [
        'sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-versioning',
    ]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development"
    ]
)
