from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="drf-serpy",
    version="0.4.3",
    description="ridiculously fast object serialization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sergenp/drf-serpy",
    author="Clark DuVall, Sergen Pekşen",
    author_email="clark.duvall@gmail.com, peksensergen@gmail.com",
    license="MIT",
    install_requires=["drf-yasg"],
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords=(
        "serialization",
        "rest",
        "json",
        "api",
        "marshal",
        "marshalling",
        "validation",
        "schema",
        "fast",
    ),
    packages=find_packages(exclude=["contrib", "docs", "tests", "benchmarks"]),
    include_package_data=True,
)
