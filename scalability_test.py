#%%
# Preparing the C++ part:
# - Read https://blog.esciencecenter.nl/irregular-data-in-pandas-using-c-88ce311cb9ef
# - Just download the existing ticcl_output_reader
#
# Preparing the Julia part:
# - You need Python with a shared library! (Arch Linux /usr/bin/python)
# - Tested on Julia 1.6.3
# - Open Julia, enter the following commands:
#   - julia> using Pkg
#   - ENV["PYTHON"] = "/path/to/python"
#   - Pkg.add("PyCall")
# - Install pyjulia with `python -m pip install julia`
# - Run `python`, `import julia`, then `julia.install("julia=julia-1.6.3")` or whatever it's called.
#   - The argument of `install` can be ignored it `julia` is your binary.

import numpy as np
import pandas as pd
import time

### PYTHON ###
def load_pandas(filename):
    df_tuples = pd.read_csv(filename,
                        sep='#', index_col=0, names=['key', 'values'],
                        converters={'values': lambda w: tuple(w.split(','))})
    df = df_tuples['values'].apply(pd.Series, 1).stack().astype('uint64').to_frame()
    df.index.rename(["key", "list_index"], inplace=True)
    df.rename({0: 'value'}, axis='columns', inplace=True)
    return df

def load_external(arrays):
    df = pd.DataFrame.from_records({
            "key": arrays[0],
            "list_index": arrays[1],
            "value": arrays[2]
        }, index=["key", "list_index"])
    return df

### JULIA ###
import julia
from julia.api import Julia
jl = Julia(runtime="julia-1.6.3")
from julia import Main
jl.eval('include("jl_reader_dict.jl")')
def load_julia_dict(filename):
    arrays = jl.eval(f'read_arrays_jl_dict("{filename}")')
    return load_external(arrays)

jl.eval('include("jl_reader_c.jl")')
def load_julia_c(filename):
    arrays = jl.eval(f'read_arrays_jl_c("{filename}")')
    return load_external(arrays)

jl.eval('include("jl_reader_manual.jl")')
def load_julia_manual(filename):
    arrays = jl.eval(f'read_arrays_jl_manual("{filename}")')
    return load_external(arrays)

### C++ ###
import ticcl_output_reader
def load_cpp(filename):
    arrays = ticcl_output_reader.load_confuslist_index(filename)
    return load_external(arrays)

#%% Warmup
filename = "gen-data/confus-001-0.txt"
Main.filename = filename
df_python = load_pandas(filename)
df_julia_c = load_julia_c(filename)
df_julia_dict = load_julia_dict(filename)
df_julia_manual = load_julia_manual(filename)
df_cpp = load_cpp(filename)

assert df_python.eq(df_julia_c).all().all()
assert df_python.eq(df_julia_dict).all().all()
assert df_python.eq(df_julia_manual).all().all()
assert df_python.eq(df_cpp).all().all()
"Success"
#%%
python_time = []
julia_c_time = []
julia_dict_time = []
julia_manual_time = []
cpp_time = []

rows = []
elements = []

N = 100
T = 5
for i in range(1, N + 1):
    for j in range(0, 10):
        filename = "gen-data/confus-{:03d}-{:d}.txt".format(i, j)
        Main.filename = filename
        for (array, load_fun) in [
                (python_time, load_pandas),
                (julia_c_time, load_julia_c),
                (julia_dict_time, load_julia_dict),
                (julia_manual_time, load_julia_manual),
                (cpp_time, load_cpp)]:
            start = time.time()
            for tries in range(0, T):
                df = load_fun(filename)
            array.append((time.time() - start) / T)

        rows.append(5 * i)
        elements.append(df.shape[0])
        perc = round(100 * (i - 1 + j / 10) / N, 1)
        print(f'perc = {perc}%')

df = pd.DataFrame({
    'rows': rows,
    'elements': elements,
    'python_time': python_time,
    'cpp_time': cpp_time,
    'julia_c_time': julia_c_time,
    'julia_dict_time': julia_dict_time,
    'julia_manual_time': julia_manual_time,
})
df.to_csv('scalability_test.csv')
# %%
load_external_time = []
read_arrays_julia_c_time = []
read_arrays_julia_dict_time = []
read_arrays_julia_manual_time = []
read_arrays_cpp_time = []

rows = []
elements = []

N = 100
T = 5
for i in range(1, N + 1):
    for j in range(0, 10):
        filename = "gen-data/confus-{:03d}-{:d}.txt".format(i, j)
        Main.filename = filename


        for (array, read_fun) in [
                (read_arrays_julia_c_time, 'read_arrays_jl_c'),
                (read_arrays_julia_dict_time, 'read_arrays_jl_dict'),
                (read_arrays_julia_manual_time, 'read_arrays_jl_manual')]:
            start = time.time()
            for tries in range(0, T):
                arrays = jl.eval(f'{read_fun}("{filename}")')
            array.append((time.time() - start) / T)

        start = time.time()
        for tries in range(0, T):
            arrays = ticcl_output_reader.load_confuslist_index(filename)
        read_arrays_cpp_time.append((time.time() - start) / T)

        start = time.time()
        for tries in range(0, T):
            df = load_external(arrays)
        load_external_time.append((time.time() - start) / T)

        rows.append(5 * i)
        elements.append(df.shape[0])
        perc = round(100 * (i - 1 + j / 10) / N, 1)
        print(f'perc = {perc}%')

df = pd.DataFrame({
    'rows': rows,
    'elements': elements,
    'load_external': load_external_time,
    'read_arrays_cpp_time': read_arrays_cpp_time,
    'read_arrays_julia_c_time': read_arrays_julia_c_time,
    'read_arrays_julia_dict_time': read_arrays_julia_dict_time,
    'read_arrays_julia_manual_time': read_arrays_julia_manual_time,
})
df.to_csv('parts_test.csv')
# %%
