from setuptools import setup, find_packages

setup(
    name='slamdring',
    version='0.1.dev',
    packages=find_packages(exclude=["data/"]),
    license='MIT',
    author="Tim Renner",
    classifiers = [
      "Development Status :: 3 - Alpha",
      "Programming Language :: Python :: 3.6"
    ],
    install_requires = [
        'click',
        'aiohttp',
    ],
    entry_points = {
        "console_scripts": ["slamdring=slamdring.slamdring:cli"]
        }
)