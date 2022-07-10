#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aioliqpay',
    version='1.0.0',
    description='Asyncio LiqPay Python3 SDK',
    packages=['aioliqpay'],
    author_email='zhltoxa@gmail.com'
)
