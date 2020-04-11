#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="k8spin_common",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'kopf'
    ]
)