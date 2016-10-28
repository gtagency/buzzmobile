#!/usr/bin/env python

#for downloading the packages needed for this project.
from setuptools import setup, find_packages

setup(
    name='buzzmobile',
    version='0.3',
    url='https://github.com/gtagency/buzzmobile',
    author='gtagency',
    license='MIT',
    keywords='car cars self-driving lidar gps ros',
    install_requires=[
        'catkin_pkg',
        'googlemaps',
        'matplotlib',
        'numpy',
        'polyline',
        'pylint',
        'pytest',
        'python-empy',
        'pyyaml',
        'rospkg',
        ],
)
