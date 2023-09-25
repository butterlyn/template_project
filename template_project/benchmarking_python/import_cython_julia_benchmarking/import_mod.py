import pandas as pd
import dask.array as da
import numpy as np
import polars as pl
import numexpr as ne
import numba

# Define a function to generate the alternating sign sequence


def _dask_alternating_sign(n):
    # Generate a sequence of alternating -1 and 1 values
    sign = da.ones(n)
    sign[1::2] = -1
    return sign


# Define a function to calculate pi using the Leibniz algorithm
def dask_calculate_pi(n):
    # Generate the series of terms using a Dask array
    i = da.arange(n)
    sign = _dask_alternating_sign(n)
    term = da.where(sign == 1, 1 / (2 * i + 1), -1 / (2 * i + 1))

    # Sum the terms
    pi_estimate = 4 * term.sum()

    return pi_estimate.compute()


# Define a function to generate the alternating sign sequence
def _python_alternating_sign(n):
    # Generate a sequence of alternating -1 and 1 values
    sign = [(-1) ** i for i in np.arange(n)]
    return sign


# Define a function to calculate pi using the Leibniz algorithm
def python_calculate_pi(n):
    # Generate the series of terms using a list comprehension
    sign = _python_alternating_sign(n)
    term = [sign[i] / (2 * i + 1) for i in np.arange(n)]

    # Sum the terms
    pi_estimate = 4 * sum(term)

    return pi_estimate


# Define a function to generate the alternating sign sequence

def _pandas_alternating_sign(n):
    # Generate a sequence of alternating -1 and 1 values
    sign = pd.Series([-1] * n)
    sign[::2] = 1
    return sign


# Define a function to calculate pi using the Leibniz algorithm
def pandas_calculate_pi(n):
    # Generate the series of terms using a pandas Series
    sign = _pandas_alternating_sign(n)
    term = sign / (2 * pd.Series(np.arange(n)) + 1)

    # Sum the terms
    pi_estimate = 4 * term.sum()

    return pi_estimate

# Define a function to generate the alternating sign sequence


# Define a function to calculate pi using the Leibniz algorithm
@numba.jit(nopython=True)
def numba_calculate_pi(n):
    pi_estimate = 0.0
    sign = 1

    for i in range(n):
        pi_estimate += sign / (2 * i + 1)
        sign = -sign

    return 4 * pi_estimate

# Define a function to generate the alternating sign sequence


def _numpy_alternating_sign(n):
    # Generate a sequence of alternating -1 and 1 values
    sign = np.ones(n)
    sign[1::2] = -1
    return sign


# Define a function to calculate pi using the Leibniz algorithm
def numpy_calculate_pi(n):
    # Generate the series of terms using a NumPy array
    i = np.arange(n)
    sign = _numpy_alternating_sign(n)
    term = np.where(sign == 1, 1 / (2 * i + 1), -1 / (2 * i + 1))

    # Sum the terms
    pi_estimate = 4 * np.sum(term)

    return pi_estimate


def numexpr_calculate_pi(n):
    # Generate the series of terms using a NumPy array
    i = np.arange(n)
    sign = _numpy_alternating_sign(n)
    term = ne.evaluate('where(sign == 1, 1 / (2 * i + 1), -1 / (2 * i + 1))')

    # Sum the terms
    pi_estimate = 4 * np.sum(term)

    return pi_estimate


# Define a function to calculate pi using the Leibniz algorithm
def polars_calculate_pi(n):
    # Generate the series of terms using a Polars series
    df = pl.DataFrame({"index": np.arange(n)}).lazy()
    df = df.with_columns(
        (-(pl.col("index") % 2) * 2 + 1).alias("sign"),
    )
    df = df.with_columns(
        (1 / ((2 * pl.col("index")) + 1)).mul(pl.col("sign")).alias("term"),
    )

    return (df.select("term").sum().collect() * 4)[0, 0]
