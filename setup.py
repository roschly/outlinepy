from typing import List
from setuptools import setup, find_packages


setup(
    name="outlinepy",
    description="Commandline tool for outlining Python code.",
    url="https://github.com/roschly/outlinepy",
    download_url="https://github.com/roschly/outlinepy/archive/refs/tags/v0.0.2.tar.gz",
    author="roschly",
    entry_points={
        "console_scripts": [
            "outlinepy = outlinepy.__main__:main",
        ]
    },
    packages=find_packages(),
    install_requires=[
        "astroid",
    ],
)
