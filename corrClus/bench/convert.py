from glob import glob

TO_CONVERT_FLOATS = ['selfesteem']
TO_CONVERT_INTS = glob("./random_*_orig")


def convert(file, t):
    data = []
    with open(file, 'r') as inf:
        for line in inf.readlines():
            if t == 'float':
                data.append([float(x) for x in line.split(' ')])
            elif t == 'int':
                data.append([float(x) for x in line.split(' ')])

    # Data should be lower triangular
    tvars = list(range(1, len(data) + 1))
    weighted_rels = []
    weight_sum = 0
    for i, dataline in enumerate(data):
        for j, weight in enumerate(dataline):
            if j < i:
                if t == 'float':
                    int_weight = weight * 100.0
                else:
                    int_weight = weight
                weighted_rels.append([i+1, j+1, int_weight])
                weight_sum += abs(int_weight)
    normalized = []
    for wij in weighted_rels:
        if t == 'float':
            normalized.append([wij[0], wij[1], int(wij[2] * 260 / weight_sum)])
        else:
            normalized.append([wij[0], wij[1], wij[2]])

    with open(file + '_benchmark', 'w') as outf:
        print(' '.join([str(x) for x in tvars]), file=outf)
        for wij in normalized:
            print("%d %d %d" % (wij[0], wij[1], wij[2]), file=outf)


if __name__ == '__main__':
    for file in TO_CONVERT_FLOATS:
        convert(file, 'float')
    for file in TO_CONVERT_INTS:
        convert(file, 'int')
