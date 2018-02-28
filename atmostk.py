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


def atmostk_bin(l, k):
    return list(map(lambda x: list(map(lambda i: -i, x)),
                    list(itertools.combinations(l, k))))


def atleastk_bin(l, k):
    return list(map(lambda x: list(x), list(itertools.combinations(l, len(l) - k))))


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

    # Add 'at least one' constraint
    clauses.extend(atleastk_bin(rangeincl(1, n), max(1, k-3)))

    return {'name': ("binary_k%d_n%d" % (k, n)),
            'nvars': n + log2n * k + n * k,
            'nclauses': len(clauses),
            'clauses': clauses}



def commander_encoding(k, n, s):
    if s < k:
        print("For commander encoding, size should be greater than constraint.")
        return

    nsets = ((n - 1) / s) + 1

    def c(i,j):
        return n + i * nsets + j

    clauses = []



    return { 'name': ("commander_k%d_n%d_s%d" % (k, n, s)),
             'nvars': n,
             'nclauses': len(clauses),
             'clauses': clauses}

def main():
    if len(sys.argv) < 4:
        print("Usage: python atmostk.py NVARS K [ENCODING=1,2]")
        return

    n = int(sys.argv[1])
    k = int(sys.argv[2])
    en = int(sys.argv[3])
    encoding = {}

    if en == 1:
        encoding = binary_encoding(k,n)
    elif en == 2:
        if len(sys.argv) < 5:
            print("For encoding 2 (commander encoding) you have to provide a size (last argument)")
            return

        s = int(sys.argv[4])
        encoding = commander_encoding(k, n, s)
    else:
        print("Unkown encoding.")
        return

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