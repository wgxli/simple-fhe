import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="simplefhe",
    version="1.0.0",
    description="Dead-simple full homomorphic encryption (FHE) for Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/wgxli/simple-fhe",
    author="Samuel Li",
    author_email="simplefhe@samuelj.li",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["simplefhe"],
    include_package_data=True,
)

