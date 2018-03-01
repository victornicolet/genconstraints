import sys
import itertools
import subprocess
from math import log2, ceil

## Encoding format:
# Dictionary contains the number of variables and then the number of clauses.
# The clauses are a list of integers.
##

def print_encoding(enc):
    file = open(enc['name'],'w')
    file.write("p cnf %d %d\n" % (enc['nvars'], enc['nclauses']))
    for clause in enc['clauses']:
        file.write(' '.join(list(map(str,clause))) + " 0\n")


def minisat(enc):
    subprocess.call(["./minisat", enc['name'], enc['name'] + ".res"])


def rangeincl(a,b):
    return range(a, b + 1)


def atleast1(n):
    return rangeincl(1, n)


def nthbit(c,n):
    return c & (1 << (n-1)) != 0


def neg_all(l):
    return list(map(lambda x: -x, l))


def atmostk_bin(l, k):
    return list(itertools.combinations(neg_all(l), k + 2))


def atleastk_bin(l, k):
    return list(itertools.combinations(l, len(l)-k))


def binary_encoding(k,n):
    OFFSET_T = n
    OFFSET_B = (k + 2) * n
    log2n = ceil(log2(n))

    def X(i):
        return i

    def T(g,i):
        return OFFSET_T + (g-1)*n + i

    def B(g,j):
        return OFFSET_B + (g-1) * log2n + j

    def Phi(i,g,j):
        if nthbit(i,j):
            return B(g,j)
        else:
            return -B(g,j)

    def headClause(i):
        clause = [-X(i)]
        for g in rangeincl(max(1, k - n + i), min(i, k)):
            clause.append(T(g, i))
        return clause

    clauses = []
    for i in rangeincl(1, n):
        clauses.append(headClause(i))
        for g in rangeincl(max(1, k - n + i), min(i, k)):
            for j in rangeincl(1, log2n):
                clauses.append([-T(g, i), Phi(i, g, j)])


    return {'name': ("binary_k%d_n%d" % (k, n)),
            'nvars': n + log2n * k + n * k,
            'nclauses': len(clauses),
            'clauses': clauses}


def commander_encoding(k, n, s):
    nsets = ceil(n/s)

    if nsets < k:
        print("For commander encoding, size should be greater than constraint.")
        return -1

    def C(i, j):
        return n + i * k + j

    clauses = []
    # For each group
    for i in range(0, nsets):
        gis = list(rangeincl(1 + i * s, min(1 + (i + 1) * s, n)))
        cis = list(map(lambda j: -C(i, j), list(rangeincl(1, k))))
        gis.extend(cis)

        clauses.extend(atmostk_bin(gis, k))
        clauses.extend(atleastk_bin(gis, k))
        # Remove symmetrical solutions by ordering commander variables
        for j in rangeincl(1, k-1):
            clauses.append([-C(i, j), C(i, j+1)])

    # Encoding cardinality on the commander variables
    # Using simply the binomial encoding since tracking new variables
    # here would require additional work
    clauses.extend(atmostk_bin(list(map(lambda ij: C(ij[0], ij[1]),
                                        list(itertools.product(range(0, nsets), rangeincl(1, k))))), k))


    return {'name': ("commander_k%d_n%d_s%d" % (k, n, s)),
            'nvars': n + nsets * k,
            'nclauses': len(clauses),
            'clauses': clauses}


def seqcount_encoding(k, n):
    clauses = []
    def R(i,j):
        return n + i * k + j
    #(1)
    for i in rangeincl(1, n):
        clauses.append([-i, R(i, 1)])
    # (2)
    for j in rangeincl(2, k):
        clauses.append([-R(1, j)])
    # (3)
    for i in rangeincl(2, n-1):
        for j in rangeincl(1, k):
            clauses.append([-R(i-1, j), R(i, j)])
    # (4)
    for i in rangeincl(2, n-1):
        for j in rangeincl(2, k):
            clauses.append([-i, -R(i-1, j-1), R(i, j)])
    # (5)
    for i in rangeincl(1,n):
        clauses.append([-i, R(i-1, k)])

    return {'name': ("seqcount_k%d_n%d" % (k, n)),
            'nvars': n + k * (n-1),
            'nclauses': len(clauses),
            'clauses': clauses}

def main():
    if len(sys.argv) < 4:
        print("Usage: python atmostk.py NVARS K [ENCODING=1,2] [SIZE if ENCODING=2]")
        return

    n = int(sys.argv[1])
    k = int(sys.argv[2])
    en = int(sys.argv[3])
    encoding = {}

    if en == 1:
        encoding = binary_encoding(k, n)
    elif en == 2:
        if len(sys.argv) < 5:
            print("For encoding 2 (commander encoding) you have to provide a size (last argument)")
            return

        s = int(sys.argv[4])
        encoding = commander_encoding(k, n, s)

    elif en == 3:
        encoding = seqcount_encoding(k, n)
    else:
        print("Unkown encoding.")
        return

    if encoding == -1:
        return

    print("Encoding done!\n")

    print_encoding(encoding)

    minisat(encoding)


def test_enc():
    enc = {
        'name' : "test",
        'nvars' : 9,
        'nclauses' : 3,
        'clauses' : [[1,2,3],[4,5,6],[7,8,9]]
    }
    print_encoding(enc)



if __name__ == "__main__":
    # test_enc()
    main()