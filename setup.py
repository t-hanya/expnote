#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='expnote',
    version='0.1.0',
    description='An experiment management tool to record facts and thoughts',
    author='Toshinori Hanya',
    url='https://github.com/t-hanya/expnote',
    license='MIT',
    packages=find_packages(include='expnote.*'),
)
