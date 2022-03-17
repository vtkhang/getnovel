#!/usr/bin/env python
"""The setup and build script for novelutils."""

import setuptools

import novelutils

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='novelutils',
    version=novelutils.__version__,
    author='Eaus',
    author_email='kdekiwis1@gmail.com',
    license='MIT License',
    description='Tool based on Scrapy framework to get novel from web site.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'setuptools>=58.0.4',
        'scrapy>=2.6.1',
        'beautifulsoup4>=4.10.0',
        'pillow>=9.0.1'
        ],
    entry_points={
        'console_scripts': ['novelutils = novelutils:run_main'],
    },
)
