import time
import timeit

n: int = 100_000_000

# time the import of calculate_pi
import_time_cython = timeit.timeit(
    "from liebnitz_calculation import cython_calculate_pi2", number=1)

from liebnitz_calculation import cython_calculate_pi2

# time the execution of calculate_pi
start_time_cython2 = time.time()
cython_result2 = cython_calculate_pi2(n)
end_time_cython2 = time.time()
calc_time_cython2 = end_time_cython2 - start_time_cython2
total_time_cython2 = import_time_cython + calc_time_cython2

julia_import_start_time = time.time()
import julia
from julia import Main

julia.install()

julia_code: str = """
function calculate_pi(n)
    pi_estimate = 0.0
    sign = 1.0
    for i in 0:n-1
        pi_estimate += sign / (2i + 1)
        sign = -sign
    end
    return 4 * pi_estimate
end
"""

Main.eval(julia_code)

julia_import_end_time = time.time()
julia_import_time = julia_import_end_time - julia_import_start_time

start_time = time.time()
julia_result = Main.calculate_pi(n)
end_time = time.time()
calc_time_julia = end_time - start_time
total_time_julia = julia_import_time + calc_time_julia

from import_mod import pandas_calculate_pi
from import_mod import python_calculate_pi
from import_mod import numba_calculate_pi
from import_mod import dask_calculate_pi
from import_mod import numpy_calculate_pi
from import_mod import polars_calculate_pi
from import_mod import numexpr_calculate_pi

start_time_pandas = time.time()
pandas_result = pandas_calculate_pi(n)
end_time_pandas = time.time()
calc_time_pandas = end_time_pandas - start_time_pandas

# time the execution of calculate_pi
start_time_numba = time.time()
numba_result = numba_calculate_pi(n)
end_time_numba = time.time()
calc_time_numba = end_time_numba - start_time_numba

# time the execution of calculate_pi
start_time_python = time.time()
python_result = python_calculate_pi(n)
end_time_python = time.time()
calc_time_python = end_time_python - start_time_python


# time running dask version
import_time_dask = timeit.timeit(
    "from import_mod import dask_calculate_pi", number=1)


# time the execution of calculate_pi
start_time_dask = time.time()
dask_result = dask_calculate_pi(n)
end_time_dask = time.time()
calc_time_dask = end_time_dask - start_time_dask


# time running numpy version
import_time_numpy = timeit.timeit(
    "from import_mod import numpy_calculate_pi", number=1)

# time the execution of calculate_pi
start_time_numpy = time.time()
numpy_result = numpy_calculate_pi(n)
end_time_numpy = time.time()
calc_time_numpy = end_time_numpy - start_time_numpy

# time running polars version
import_time_polars = timeit.timeit(
    "from import_mod import polars_calculate_pi", number=1)


# time the execution of calculate_pi
start_time_polars = time.time()
polars_result = polars_calculate_pi(n)
end_time_polars = time.time()
calc_time_polars = end_time_polars - start_time_polars


# time running numexpr version
import_time_numexpr = timeit.timeit(
    "from import_mod import numexpr_calculate_pi", number=1)


# time the execution of calculate_pi
start_time_numexpr = time.time()
numexpr_result = numexpr_calculate_pi(n)
end_time_numexpr = time.time()
calc_time_numexpr = end_time_numexpr - start_time_numexpr

print("CYTHON")
# print(f"Import time: {import_time_cython:.6f} seconds")
print(f"Calculation time: {calc_time_cython2:.6f} seconds")
print(f"Import time: {import_time_cython:.6f} seconds")
print(f"Total time: {total_time_cython2:.6f} seconds")
print(f"Returned value: {cython_result2}")
print()
print("DASK")
# print(f"Import time: {import_time_dask:.6f} seconds")
print(f"Calculation time: {calc_time_dask:.6f} seconds")
# print(f"Total time: {import_time_dask + calc_time_dask:.6f} seconds")
print(f"Returned value: {dask_result}")
print()
print("NUMPY")
# print(f"Import time: {import_time_numpy:.6f} seconds")
print(f"Calculation time: {calc_time_numpy:.6f} seconds")
# print(f"Total time: {import_time_numpy + calc_time_numpy:.6f} seconds")
print(f"Returned value: {numpy_result}")
print()
print("POLARS")
# print(f"Import time: {import_time_polars:.6f} seconds")
print(f"Calculation time: {calc_time_polars:.6f} seconds")
# print(f"Total time: {import_time_polars + calc_time_polars:.6f} seconds")
print(f"Returned value: {polars_result}")
print()
print("NUMEXPR")
# print(f"Import time: {import_time_numexpr:.6f} seconds")
print(f"Calculation time: {calc_time_numexpr:.6f} seconds")
# print(f"Total time: {import_time_numexpr + calc_time_numexpr:.6f} seconds")
print(f"Returned value: {numexpr_result}")
print()
print("NUMBA")
print(f"Calculation time: {calc_time_numba:.6f} seconds")
print(f"Returned value: {numba_result}")
print()
print("PYTHON")
print(f"Calculation time: {calc_time_python:.6f} seconds")
print(f"Returned value: {python_result}")
print()
print("PANDAS")
print(f"Calculation time: {calc_time_pandas:.6f} seconds")
print(f"Returned value: {pandas_result}")
print()
print("JULIA")
print(f"Calculation time: {calc_time_julia:.6f} seconds")
print(f"Import time: {julia_import_time:.6f} seconds")
print(f"Total time: {total_time_julia:.6f} seconds")
print(f"Returned value: {julia_result}")
print()
