import correlation_clustering as ccs
import glob

BENCHMARKS = './bench/*_benchmark'
CSV_HEADER = "id,#points,#weights,#clauses,#clusters,timeout,solving time (s)," \
             "encoding time (s),cluster construction time (s),memory(MB)"

def bench():
    all_benchmarks = glob.glob(BENCHMARKS)
    results = []
    for benchmark in all_benchmarks:
        ccs_instance = ccs.solve(benchmark, timeout=500)
        print(ccs_instance)
        results.append([ccs_instance.file, len(ccs_instance.data_points), len(ccs_instance.weights),
                        len(ccs_instance.clauses), len(ccs_instance.clusters), ccs_instance.timed_out, ccs_instance.solve_time,
                        ccs_instance.encode_time, ccs_instance.cluster_time, ccs_instance.solve_memory])

    with open("results.csv", 'a') as fp:
        # print(CSV_HEADER, file=fp)
        for point in results:
            print(",".join([str(x) for x in point]), file=fp)
        fp.close()


if __name__ == '__main__':
    bench()