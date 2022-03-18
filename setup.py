# Author: Toshiaki Asakura <aflu.blossompaws@gmail.com>
# Copyright (c) 2021 Toshiaki Asakura
# License : MIT license

from setuptools import setup

DESCRIPTION = "py_simple_report: Produce elemnts of figure files and number/pecentage contained csv file for a report."
NAME = "py_simple_report"
AUTHOR = "Toshiaki Asakura"
AUTHOR_EMAIL = "aflu.blossompaws@gmail.com"
URL = "https://github.com/toshiakiasakura/py_simple_report"
LICENSE = "MIT"
DOWNLOAD_URL = "https://github.com/toshiakiasakura/py_simple_report"
PYTHON_REQUIRES = ">=3.7"

INSTALL_REQUIRES = [
    'matplotlib',
    'numpy>=1.20.3',
    'pandas>=1.2.4',
    'cmocean>=2.0',
    'japanize_matplotlib'
] 

EXTRAS_REQUIRE = {}

PACKAGES = [
    "py_simple_report"
]

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Multimedia :: Graphics',
    'Framework :: Matplotlib',
]

with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(name=NAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=AUTHOR,
      maintainer_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=long_description,
      license=LICENSE,
      url=URL,
      download_url=DOWNLOAD_URL,
      python_requires=PYTHON_REQUIRES,
      install_requires=INSTALL_REQUIRES,
      setup_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      packages=PACKAGES,
      classifiers=CLASSIFIERS
    )
