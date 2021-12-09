import julia
import pandas as pd
import ticcl_output_reader

from julia.api import Julia
jl = Julia(runtime="julia-1.6.4")
jl.eval('using Pkg')
jl.eval('Pkg.activate(".")')
from julia import Main
jl.eval('include("src/julia/jl_reader_c.jl")')
jl.eval('include("src/julia/jl_reader_dict.jl")')
jl.eval('include("src/julia/jl_reader_manual.jl")')

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

def read_arrays_julia_c(filename):
    return jl.eval(f'read_arrays_jl_c("{filename}")')

def read_arrays_julia_basic(filename):
    return jl.eval(f'read_arrays_jl_dict("{filename}")')

def read_arrays_julia_opt(filename):
    return jl.eval(f'read_arrays_jl_manual("{filename}")')

def read_arrays_cpp(filename):
    return ticcl_output_reader.load_confuslist_index(filename)