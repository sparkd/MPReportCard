
import os

try:
    from setuptools import setup
except:
    from distutils.core import setup

version = '0.1'

setup(
    name='mp_data',
    version=version,
    description='MPs.report',
    author='Ben Scott',
    author_email='ben@benscott.co.uk',
    packages=[
        'mp_data',
    ]
)