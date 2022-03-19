#!/usr/bin/env python
"""The setup and build script for novelutils."""

from setuptools import setup, find_packages
import pkg_resources

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="novelutils",
    version=pkg_resources.require("novelutils")[0].version,
    author="Eaus",
    author_email="kdekiwis1@gmail.com",
    license="MIT License",
    description="Tool based on Scrapy framework to get novel from web site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages("novelutils"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Scrapy==2.5.1",
        "beautifulsoup4>=4.10.0",
        "Pillow>=8.4.0",
    ],
    extras_require={
        "dev": [
            "pylint>=2.12.2",
            "yapf>=0.32.0",
        ]
    },
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["novelutils = novelutils:run_main"],
    },
)
