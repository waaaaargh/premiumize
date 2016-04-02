#!/usr/bin/env python3

from distutils.core import setup

setup(name="premiumize",
      version="0.0.1",
      description="Unofficial python bindings for the premiumize.me API",
      author="Johanes Fürmann",
      author_email="johannes@weltraumpflege.org",
      url="https://github.com/waaaaargh/premiumizepy",

      install_requires=[
          'requests'
      ],

      packages=[
          'premiumize',
      ]
)
