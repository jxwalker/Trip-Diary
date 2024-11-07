from setuptools import setup, find_packages

setup(
    name="trip_diary",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pytest',
        'pytest-cov',
    ],
)