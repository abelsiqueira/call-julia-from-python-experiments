function gen_confus(;
  filename = "confus.txt",
  n_rows = 50,
  col_max = 5000,
)
  keys = sort(rand(100_000:999_999, n_rows))
  while !allunique(keys)
    keys = unique(keys)
    keys = sort([keys; rand(1:100_000, n_rows - length(keys))])
  end
  n_elem = 0
  open(filename, "w") do io
    for i = 1:n_rows
      n_cols = rand(1:col_max)
      n_elem += n_cols
      cols = sort(rand(100_000:999_999, n_cols))
      line = string(keys[i]) * "#" * join(cols, ",")
      println(io, line)
    end
  end

  return n_elem
end