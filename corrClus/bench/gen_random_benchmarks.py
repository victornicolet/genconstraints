# Script to generate 100 random benchmarks with increasing number of variables
from random import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 gen_random_benchmarks.py NUM_OF_BENCHMARKS")
        exit(0)
    for benchno in range(10, int(sys.argv[1])):
        weights = []
        for i in range(0, benchno):
            wline = []
            for j in range(0, i):
                wline.append(randint(-10, 10))
            wline.append(1)
            weights.append(wline)

        benchname = 'random_%d_orig' % benchno

        with open(benchname, 'w') as benchfile:
            for wline in weights:
                print(' '.join([str(x) for x in wline]), file=benchfile)
            benchfile.close()

