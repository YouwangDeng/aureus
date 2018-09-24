#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aureus',
    version='0.0.3',
    description=(
        'a simple python web framework'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Youwang Deng',
    author_email='dengyouwang@gmail.com',
    maintainer='Youwang Deng',
    maintainer_email='dengyouwang@gmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/YouwangDeng/aureus',
    install_requires=[
        'Werkzeug>=0.14.1',
        'PyMySQL>=0.9.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)