#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='liqpay-sdk-python3',
    version='1.0.1',
    description='LiqPay Python3 SDK',
    long_description=long_description,
    url="https://github.com/aorzh/liqpay-sdk-python3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests']
)
