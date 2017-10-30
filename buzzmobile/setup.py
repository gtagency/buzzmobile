#!/usr/bin/env python
"""Python setup environment for buzzmobile."""

# for downloading the packages needed for this project.
from setuptools import setup

TEST_REQUIRES = [
        'pytest==3.0.3',
        'netifaces==0.10.5',
        'pyrostest>=0.1.2',
        ]

setup(
    name='buzzmobile',
    version='0.3.1',
    url='https://github.com/gtagency/buzzmobile',
    author='gtagency',
    license='MIT',
    keywords='car cars self-driving lidar gps ros',
    install_requires=[
        'catkin_pkg==0.2.10',
        'googlemaps==2.4.4',
        'matplotlib==1.5.3',
        'numpy==1.11.2',
        'polyline==1.3.1',
        'pylint',
        'pyyaml==3.12',
        'rospkg==1.0.41',
        'ds4drv', # requires apt-get install python-dev
        'empy==3.3.2', # required to make catkin_make work
        ] + TEST_REQUIRES,
)
