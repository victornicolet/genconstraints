# Correlation clustering

## Benchmarks
In the `./bench` folder, you can generate random benchmarks by executing the python script:
```python3 bench.py```
Then, convert the correlation matrix files to the encoder input format:
```python3 convert.py```
Now back in this folder (`corrClus`) you can execute the benchmarking script:
```python3 bench.py NUMBER_OF_BENCHMARKS```

## Tests
There are a few correctness tests in the `tests` folder. If you want to check the correctness of `solve` after a
modification, execute the `test.py` script.