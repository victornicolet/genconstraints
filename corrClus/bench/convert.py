from glob import glob

TO_CONVERT = ['selfesteem']
TO_CONVERT.extend(glob("./random_*_orig"))

def convert(file):
    data = []
    with open(file, 'r') as inf:
        for line in inf.readlines():
            data.append([float(x) for x in line.split(' ')])
    # Data should be lower triangular
    tvars = list(range(1, len(data) + 1))
    weighted_rels = []
    weight_sum = 0
    for i, dataline in enumerate(data):
        for j, weight in enumerate(dataline):
            if j < i:
                int_weight = weight * 1000.0
                weighted_rels.append([i+1, j+1, int_weight])
                weight_sum += abs(int_weight)
    normalized = []
    for wij in weighted_rels:
        normalized.append([wij[0], wij[1], int(wij[2] * 260 / weight_sum)])

    with open(file + '_benchmark', 'w') as outf:
        print(' '.join([str(x) for x in tvars]), file=outf)
        for wij in normalized:
            print("%d %d %d" % (wij[0], wij[1], wij[2]), file=outf)


if __name__ == '__main__':
    for file in TO_CONVERT:
        convert(file)
