"""PyFileDB setup configuration."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyfiledb",
    version="1.0.0",
    description="Python dosya tabanli veritabani kutuphanesi - Siteler icin dosya ve dis depolama destegi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PyFileDB",
    python_requires=">=3.8",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pyfiledb=pyfiledb.app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
    ],
)
