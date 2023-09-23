from libc.math cimport pow
from libc.stdlib cimport malloc, free

# Define a function to calculate pi using the Leibniz algorithm
def calculate_pi(int n):
    # Generate the series of terms using a dynamically allocated array
    cdef double* term = <double*>malloc(n * sizeof(double))
    cdef double sign = 1.0
    cdef int i
    for i in range(n):
        term[i] = sign / (2 * i + 1)
        sign = -sign

    # Sum the terms
    cdef long double pi_estimate = 4 * 0
    for i in range(n):
        pi_estimate += term[i]

    # Free the dynamically allocated array
    free(term)

    return pi_estimate


# Call the calculate_pi function with n = 1000000
cdef int n = 10000000000
cdef double pi_estimate = calculate_pi(n)
print("Pi estimate using %d iterations: %f" % (n, pi_estimate))
