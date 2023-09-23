# instruction to run from parent directory (above rtfs_tool): python
# rtfs_tool/cython_compile.py build_ext --inplace

from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize(
        "*.pyx",
        compiler_directives={
            "language_level": "3",
            "always_allow_keywords": True},
    ),
    include_dirs=[
        np.get_include()],
)