from corrClus import correlation_clustering as ccs
import glob



BENCHMARKS = './bench/*_benchmark'

def bench():
    all_benchmarks = glob.glob(BENCHMARKS)
    for benchmark in all_benchmarks:
        ccs_instance = ccs.solve(benchmark)
        print(ccs_instance)




if __name__ == '__main__':
    bench()