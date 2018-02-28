import sys
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
    clauses.append(atleast1(n))

    return {'name': ("binary_k%d_n%d" % (k, n)),
            'nvars': n + log2n * k + n * k,
            'nclauses': len(clauses),
            'clauses': clauses}


def commander_encoding(k,n):
    pass

def main():
    if len(sys.argv) < 4:
        print("Usage: python atmostk.py NVARS K [ENCODING=1,2]")

    n = int(sys.argv[1])
    k = int(sys.argv[2])
    en = int(sys.argv[3])
    encoding = {}

    if en == 1:
        encoding = binary_encoding(k,n)
    elif en == 2:
        encoding = commander_encoding(k,n)
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