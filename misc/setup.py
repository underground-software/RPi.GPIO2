#!/bin/env python3

from setuptools import setup, find_packages
setup(
    name="libgpiod-python-rpi",
    version="0.1",
    scripts=['say_hello.py'],

    # metadata to display on PyPI
    author="Me",
    author_email="Fedora-RPi@googlegroups.com",
    description="",
    keywords="libgpiod rpi gpio compatibility",
    url="rpi.pending.name",   # project home page, if any
    license='GPLv3',
    zip_safe=False)
)
