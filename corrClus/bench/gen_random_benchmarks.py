# Script to generate 100 random benchmarks with increasing number of variables
from random import *


if __name__ == '__main__':
    for benchno in range(10,110):
        weights = []
        for i in range(0, benchno):
            wline = []
            for j in range(0, i):
                wline.append(float(randint(-50, 50)) / 50.0)
            wline.append(1)
            weights.append(wline)

        benchname = 'random_%d_orig' % benchno

        with open(benchname, 'w') as benchfile:
            for wline in weights:
                print(' '.join([str(x) for x in wline]), file=benchfile)
            benchfile.close()

