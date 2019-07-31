# !/usr/bin/env python
from setuptools import setup

setup(
    name='ansible-selvpc-modules',
    version='1.2.0',
    description='Ansible modules for Selectel VPC platform',
    author='Rutskiy Daniil',
    author_email='rutskiy@selectel.ru',
    packages=["ansible/modules/selvpc",
              "ansible/module_utils/selvpc_utils"],
    install_requires=[
        'ansible>=2.6.18',
        'python-selvpcclient==1.0'
    ],
)

