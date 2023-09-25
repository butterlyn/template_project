# Import the ctypes library
from cpython cimport array
from libc.math cimport fabs
import numpy as np
cimport numpy as np


# Define a function to calculate pi using the Leibniz algorithm
def cython_calculate_pi2(int n) -> float:
    cdef int i
    cdef double pi_estimate = 0.0
    cdef int sign = 1

    for i in range(n):
        pi_estimate += sign / (2 * i + 1)
        sign = -sign

    return 4 * pi_estimate