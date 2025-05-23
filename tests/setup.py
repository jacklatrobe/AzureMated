"""
Setup script for FabricFriend testing
"""

from setuptools import setup, find_packages

setup(
    name="fabricfriend-tests",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-cov",
    ],
    python_requires=">=3.8",
)
