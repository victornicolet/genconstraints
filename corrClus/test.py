import glob
from . import correlation_clustering

TEST_FILES = 'tests/*clusters'
RESULT_SUFFIX = '.out'


def parse_results(finput):
    with open(finput + RESULT_SUFFIX, 'r') as res:
        clusters = []
        for line in res.readlines():
            clusters.append({int(x) for x in line.split(' ')})
    return clusters

def same_clustering(c1, c2):
    assert len(c1) == len(c2)
    for c in c1:
        assert c in c2


def main():
    testinputs = glob.glob(TEST_FILES)
    for finput in testinputs:
        ccs = correlation_clustering.solve(finput)
        clusters = parse_results(finput)
        assert same_clustering(ccs.clusters, clusters)

if __name__ == "__main__":
        main()