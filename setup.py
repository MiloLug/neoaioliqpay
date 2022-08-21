#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='neoliqpay',
    version='3.0.0',
    description='Asyncio LiqPay Python3 SDK',
    packages=['neoliqpay'],
    author_email='mistickusya.2012@gmail.com'
)
