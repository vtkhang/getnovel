# -*- coding: utf-8 -*-
"""Test the find packages function.
"""
from pathlib import Path

import setuptools

p = setuptools.find_packages(where=str(Path(__file__).parents[1]))

print(p)
