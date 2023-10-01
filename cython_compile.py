# `python cython_compile.py build_ext --inplace`

from setuptools import setup
import os
import pyMSVC
from Cython.Build import cythonize
import numpy as np

environment = pyMSVC.Environment()
os.environ.update(environment)

setup(
    ext_modules=cythonize(
        "**/*.pyx",
        compiler_directives={
            "language_level": "3",
            "always_allow_keywords": True,
        },
    ),
    include_dirs=[
        np.get_include(),
    ],
)
