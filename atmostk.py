import sys
import itertools
import subprocess
from math import log2, ceil


BUCKET_COMMANDER = 5



def binary_encoding(k, lit, dec):
    n = len(lit)
    OFFSET_T = dec
    OFFSET_B = OFFSET_T + (n + 1) * k
    log2n = ceil(log2(n))

    def X(i):
        return lit[i]

    def T(g,i):
        return OFFSET_T + g * n + i

    def B(g,j):
        return OFFSET_B + g * log2n + j

    def Phi(i,g,j):
        if nthbit(i,j):
            return B(g,j)
        else:
            return -B(g,j)

    def headClause(i):
        clause = [-X(i)]
        for g in range(max(0, k - n + i), min(i + 1, k)):
            clause.append(T(g, i))
        return clause

    clauses = []
    for i in range(0, n):
        clauses.append(headClause(i))
        for g in range(max(0, k - n + i), min(i + 1, k)):
            for j in range(0, log2n):
                clauses.append([-T(g, i), Phi(i, g, j)])


    return {'name': ("binary_k%d_n%d" % (k, n)),
            'nvars': 2*n+ (log2n + n) * k,
            'nclauses': len(clauses),
            'clauses': clauses}


def commander_encoding(k, lit, s, dec):
    n = len(lit)
    nsets = ceil(n/s)

    if nsets < k:
        print("For commander encoding, size should be greater than constraint.")
        return -1

    def C(i, j):
        return dec + i * k + j

    clauses = []
    # For each group
    for i in range(0, nsets):
        gis = [lit[j] for j in list(range(i * s, min((i + 1) * s, n)))]
        cis = [-C(i, j) for j in list(range(0, k))]
        gis.extend(cis)

        clauses.extend(atmostk_bin(gis, k))
        clauses.extend(atleastk_bin(gis, k))
        # Remove symmetrical solutions by ordering commander variables
        for j in range(0, k-1):
            clauses.append([-C(i, j), C(i, j+1)])

    # Encoding cardinality on the commander variables
    # Using simply the binomial encoding since tracking new variables
    # here would require additional work
    clauses.extend(atmostk_bin(list(map(lambda ij: C(ij[0], ij[1]),
                                        list(itertools.product(range(0, nsets), range(0, k))))), k))


    return {'name': ("commander_k%d_n%d_s%d" % (k, n, s)),
            'nvars': n + nsets * k,
            'nclauses': len(clauses),
            'clauses': clauses}


def seqcount_encoding(k, lit, dec):
    clauses = []
    n = len(lit)
    def R(i,j):
        return dec + i * k + j

    clauses.append([-lit[0], R(1,1)])
    for j in rangeincl(2, k):
        clauses.append([-R(1, j)])

    for i in rangeincl(2,n-1):
        clauses.append([-lit[i-1], R(i, 1)])
        clauses.append([-R(i-1, 1), R(i, 1)])
        for j in rangeincl(2,k):
            clauses.append([-lit[i-1], -R(i-1, j-1), R(i, j)])
            clauses.append([-R(i-1, j), R(i, j)])
        clauses.append([-lit[i - 1], -R(i - 1, k)])
    clauses.append([-lit[n-1], -R(n - 1, k)])


    return {'name': ("seqcount_k%d_n%d" % (k, n)),
            'nvars': n + n * k + k,
            'nclauses': len(clauses),
            'clauses': clauses}


def encode(en, k, lit, dec):
    if en == 1:
        return binary_encoding(k, lit, dec)
    elif en == 2:
        return commander_encoding(k, lit, BUCKET_COMMANDER, dec)
    elif en == 3:
        return seqcount_encoding(k, lit, dec)
    else:
        print("Unkown encoding.")
        return -1


def encode_exact_k(en, k, lits):
    atmostk = encode(en, k, lits, len(lits) + 1)
    atleastk = encode(en, abs(len(lits) - k), neg_all(lits), atmostk['nvars'] + 1)
    return {
        'name': "exactk_" + atmostk['name'],
        'nvars': atmostk['nvars'] + atleastk['nvars'] - len(lits),
        'nclauses': atmostk['nclauses'] + atleastk['nclauses'],
        'clauses': atmostk['clauses'] + atleastk['clauses']
    }

def encode_propagation_experiment(en, k, lits):
    atmostk = encode(en, k, lits, len(lits) + 1)
    atmostk['clauses'].extend([[x] for x in lits[len(lits)-(k+1):]])
    atmostk['nclauses'] = atmostk['nclauses'] + k + 1
    atmostk['name'] = "propagation_" + atmostk['name']
    return atmostk


def main():
    if len(sys.argv) < 4:
        print("Usage: python atmostk.py K [ENCODING=1,2,3] [N] [SEQUENCE OF LITERALS]")
        return

    k = int(sys.argv[1])
    en = int(sys.argv[2])
    n = int(sys.argv[3])

    if len(sys.argv) == 4:
        literals = list(range(1, n))
    else:
        literals = [int(x) for x in sys.argv[4:]]

    # encoding = encode_exact_k(en, k, literals)
    encoding = encode_propagation_experiment(en, k, literals)

    print("Encoding done!\n")
    print_encoding(encoding)
    minisat(encoding)
    count_res(encoding['name'] + '.res', len(literals))

def test_enc():
    enc = {
        'name': "test",
        'nvars': 9,
        'nclauses': 3,
        'clauses': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    }
    print_encoding(enc)

def count_res(file, n):
    with open(file, 'r') as of:
        contents = of.readlines()
        if len(contents) > 1:
            issat = [int(x) for x in contents[1].split(' ')]
            print("TRUE Literals: %d" % len(list(filter(lambda x: x > 0, issat[:n]))))







if __name__ == "__main__":
    # test_enc()
    main()

# ***************************************************************************************
# ****               Utility functions                                                 **
# ***************************************************************************************

## Encoding format:
# Dictionary contains the number of variables and then the number of clauses.
# The clauses are a list of integers.
##
def print_encoding(enc):
    file = open(enc['name'],'w')
    file.write("p cnf %d %d\n" % (enc['nvars'], enc['nclauses']))
    for clause in enc['clauses']:
        file.write(' '.join(list(map(str,clause))) + " 0\n")


def absadd(a,b):
    if a > 0:
        return a + b
    else:
        return a - b


# Shift the values in the encoding.
# Values from 1 to n are shifted by shifta
# Values from n are shifted by shiftb
def shift_encoding(enc, n, shifta, shiftb):
    def shiftc(i):
        iid = abs(i)
        if iid in rangeincl(1,n):
            return absadd(i, shifta)
        else:
            return absadd(i, shiftb)

    newpb = []
    for clause in enc['clauses']:
        newpb.append(list(map(shiftc, clause)))


def reverse_n(enc, n):
    def ren(i):
        if i <= n:
            return -i
        else:
            return i

    enc['clauses'] = [[ren(lit) for lit in clause] for clause in enc['clauses']]

    return enc



# Combine two encodings where n1 is the original numbers of variables in enc1
# and n2 in enc2. Some auxiliary variables may have been created in the encodings
# and some space might be needed because of other variables (delta)
def combine_encodings(enc1, enc2, n1, n2, delta):
    if delta > 0:
        shift_encoding(enc1, n1, 0, n1 - delta)
        shift_encoding(enc2, n2, 0, n2 - delta)
    shift_encoding(enc2, n2 + delta, 0, int(enc1['nvars']) - n1)


def minisat(enc):
    subprocess.call(["./minisat", enc['name'], enc['name'] + ".res"])


def rangeincl(a,b):
    return range(a, b + 1)


def atleast1(n):
    return rangeincl(1, n)


def nthbit(c,n):
    return c & (1 << n) != 0


def neg_all(l):
    return list(map(lambda x: -x, l))


def atmostk_bin(lit, k):
    return list(itertools.combinations(neg_all(lit), k + 2))


def atleastk_bin(lit, k):
    return list(itertools.combinations(lit, len(lit)-k))
