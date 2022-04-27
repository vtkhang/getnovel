#!/usr/bin/env python
"""The setup and build script for getnovel."""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    setup(
        name="getnovel",
        version="1.2.1",
        author="Vũ Thừa Khang",
        author_email="vuthuakhangit@gmail.com",
        description="Tool based on Scrapy framework to get novel from websites.",
        long_description=fh.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/vtkhang/getnovel",
        project_urls={
            "Bug Tracker": "https://github.com/vtkhang/getnovel/issues",
        },
        packages=["getnovel"],
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Operating System :: OS Independent",
        ],
        include_package_data=True,
        python_requires=">=3.7",
        install_requires=[
            "scrapy == 2.5.1",
            "beautifulsoup4",
            "pillow",
            "importlib-resources",
            "importlib-metadata",
            "tldextract",
            "validators",
        ],
        extras_require={
            "dev": ["black", "ipython", "flake8"],
            "build": ["build"],
        },
        entry_points={
            "console_scripts": ["getnovel = getnovel:run_main"],
        },
    )
