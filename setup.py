from setuptools import setup, find_packages
import os, sys

setup(name='dailymotion',
      version='0.2.5',
      description='Dailymotion API SDK',
      long_description='Dailymotion API SDK',
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3"
        ],
      keywords=['dailymotion', 'api', 'sdk', 'graph'],
      author='Samir AMZANI',
      author_email='samir.amzani@gmail.com',
      url='http://github.com/dailymotion/dailymotion-sdk-python',
      license='Apache License, Version 2.0',
      include_package_data=True,
      zip_safe=False,
      py_modules = ['dailymotion','xupload'],
      setup_requires=["wheel"],
      install_requires=[
          'requests',
          'requests_toolbelt',
          'aiohttp!=4.0.0a1;python_version>"3.4"',
          'aiofiles;python_version>"3.4"',
          'asyncio;python_version>"3.4"'
      ],
)
