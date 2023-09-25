# `python cython_compile.py build_ext --inplace`

from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize(
        "src/**/*.pyx",
        compiler_directives={
            "language_level": "3",
            "always_allow_keywords": True,
        },
    ),
    include_dirs=[
        np.get_include(),
    ],
)
