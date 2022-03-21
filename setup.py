#!/usr/bin/env python
"""The setup and build script for getnovel."""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    setup(
        name="novelutils",
        version="1.2.0",
        author_email="kdekiwis1@gmail.com",
        description="Tool based on Scrapy framework to get novel from web site.",
        long_description=fh.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/estraug/novelutils",
        packages=["novelutils"],
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        include_package_data=True,
        python_requires=">=3.7",
        install_requires=[
            "scrapy == 2.5.1",
            "beautifulsoup4 >= 4.10.0",
            "Pillow >= 9.0.1",
        ],
        extras_require={
            "dev": [
                "pylint >= 2.12.2",
                "black >= 22.1.0",
                "ipython >= 7.32.0",
            ]
        },
        entry_points={
            "console_scripts": ["novelutils = novelutils:run_main"],
        },
    )
