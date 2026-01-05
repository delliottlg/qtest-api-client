"""
Setup configuration for qtest-api-client
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="qtest-api-client",
    version="1.0.0",
    author="Dave Elliott",
    author_email="delliott@lingraphica.com",
    description="Python client library for qTest Manager REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/delliottlg/qtest-api-client",
    py_modules=["qtest_client"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)
