#!/usr/bin/env python
from setuptools import setup, find_packages

setup (
  name = "tone_poem",
  version = "0.1",
  description="A thing.",
  author="valrus",
  author_email="", # Removed to limit spam harvesting.
  url="",
  package_dir = {'': 'src'},
  packages = find_packages("src", exclude="tests"),
  install_requires = ["mingus"],
  zip_safe = True
)
