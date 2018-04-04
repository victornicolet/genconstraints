import glob
from corrClus import correlation_clustering

TEST_FILES = 'tests/*clusters'
RESULT_SUFFIX = '.out'


def parse_results(finput):
    with open(finput + RESULT_SUFFIX, 'r') as res:
        clusters = []
        for line in res.readlines():
            clusters.append({int(x) for x in line.split(' ')})
    return clusters

def same_clustering(c1, c2):
    if len(c1) != len(c2):
        return False
    for c in c1:
        if c not in c2:
            return False
    return True


def main():
    testinputs = glob.glob(TEST_FILES)
    for finput in testinputs:
        ccs = correlation_clustering.solve(finput)
        clusters = parse_results(finput)
        if same_clustering(ccs.clusters, clusters):
            print("PASSED %s" % finput)
        else:
            print("FAILED %s" % finput)
            print("Expected: %s" % str(clusters))
            print("Found : %s" % str(ccs.clusters))

if __name__ == "__main__":
        main()