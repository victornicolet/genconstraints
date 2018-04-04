import sys
import subprocess
import time

MAXSAT_SOLVER = 'maxhs'
DIMACS_SUFFIX = '.xdimacs'
OUT_SUFFIX = '.out'
MAXSAT_TOP_WEIGHT = 263


class MaxSATInstanceException(Exception):
    def __init__(self, msg):
        self.message = msg


class MaxSATInstance(object):
    def __init__(self, pvars, clauses):
        n = len(pvars)
        self.vars = pvars
        self.clauses = clauses
        self.top = MAXSAT_TOP_WEIGHT
        self.nbvar = (n *  (n -1)) / 2
        self.nbclauses = len(clauses)

        # Check weights
        sumw = 0
        maxw = 0
        for c in clauses:
            w = c[0]
            sumw += w
            maxw = max(w, maxw)

        if sumw >= MAXSAT_TOP_WEIGHT:
            raise MaxSATInstanceException("Instance with sum weights > %d" % MAXSAT_TOP_WEIGHT)

    def print_to_file(self, filename):
        with open(filename, 'w') as outf:
            print("p wcnf %d %d %d" % (self.nbvar, self.nbclauses, self.top), file=outf)

            for ic, clause in enumerate(self.clauses):
                weight = clause[0]
                # if it's a hard clause
                if weight <= 0:
                    weight = self.top
                print("%d %s 0" % (weight, ' '.join([str(i) for i in clause[1]])), file=outf)


class CorrelationClusteringInstance(object):

    def __init__(self, file, data_points, weights):
        self.encode_time = 0.0
        self.solve_time = 0.0
        self.cluster_time = 0.0
        self.solve_memory = 0
        self.timed_out = False
        self.file = file
        self.data_points = data_points
        self.weights = weights
        self.clauses = []
        self.clusters = []

    def add_join(self, pair):
        a = pair[0]
        b = pair[1]
        joins = {a, b}
        new_clusters = []
        for cluster in self.clusters:
            if a in cluster or b in cluster:
                joins = joins.union(cluster)
            else:
                new_clusters.append(cluster)

        new_clusters.append(joins)
        self.clusters = new_clusters

    def add_diff(self, pair):
        a = pair[0]
        b = pair[1]
        ajoins = {a}
        bjoins = {b}

        new_clusters = []
        for cluster in self.clusters:
            if a in cluster:
                ajoins = ajoins.union(cluster)
            elif b in cluster:
                bjoins = bjoins.union(cluster)
            else:
                new_clusters.append(cluster)

        new_clusters.append(ajoins)
        new_clusters.append(bjoins)
        self.clusters = new_clusters

    def pair_lit(self, i, j):
        return i * len(self.data_points) + j

    def create_maxsat_instance(self):
        start = time.time()
        weighted_clauses = []
        clustering_cst = []
        zeroes = 0
        n = len(self.data_points)
        for i in range(0, n):
            for j in range(i + 1, n):
                wij = self.pair_lit(i, j)
                # Add the weighted literal or its negation if its weight is non zero.
                w = self.weights[i][j]
                if w != 0:
                    weighted_clauses.append((abs(w), [wij if w > 0 else -wij]))
                else:
                    zeroes += 1
                for k in range(0, n):
                    if k != j and k != i:
                        wik = self.pair_lit(i, k) if k > i else self.pair_lit(k, i)
                        wjk = self.pair_lit(j, k) if k > j else self.pair_lit(k, j)
                        if wij > wik:
                            clustering_cst.append((-1, [-wij, -wik, wjk]))
                        if wij > wjk:
                            clustering_cst.append((-1, [-wij, -wjk, wik]))

        self.encode_time = time.time() - start
        self.clauses = weighted_clauses + clustering_cst
        n = len(self.data_points)
        print(len(self.clauses) - (int((n*(n-2)*(n-1))/2) + int(n * (n-1) / 2)) + zeroes)

    def __str__(self):
        if len(self.data_points) < 20:
            return ("== FILE %s:\n%d data points (%d clauses):\n%s\nWeights:\n%s\n\n%d clusters:\n%s\nTIME:%s\t%s\t%s" %
                    (self.file,
                      len(self.data_points),
                      len(self.clauses),
                     " ".join([str(x) for x in self.data_points]),
                     "\n".join([' '.join([pnz(i) for i in x]) for x in self.weights]),
                     len(self.clusters),
                     " ".join([str(c) for c in self.clusters]),
                     "encoding %4.4f s" % self.encode_time,
                     "solving %4.4f s" % self.solve_time,
                     "cluster construction %4.4f s" % self.cluster_time))
        else:
            return "== FILE %s:\n%d data points (%d clauses), %d clusters found.\nTIME:%s\t%s\t%s" % \
                   (self.file,
                   len(self.data_points), len(self.clauses), len(self.clusters),
                    "encoding %4.4f s" % self.encode_time,
                    "solving %4.4f s" % self.solve_time,
                    "cluster construction %4.4f s" % self.cluster_time)



class FileInputError(Exception):
    def __init__(self, inputfilename, expression, message):
        self.inputfilename = inputfilename
        self.expression = expression
        self.message = message

    def __str__(self):
        return "In %s, %s : '%s'" % (self.inputfilename, self.message, self.expression)


def pnz(i):
    if i != 0:
        return str(i)
    else:
        return "_"


def maxhs(infile, timeout):
    outfile = infile + OUT_SUFFIX
    with open(outfile, 'w') as of:
        try:
            subprocess.call([MAXSAT_SOLVER, infile], stdout=of, timeout=timeout)
        except subprocess.TimeoutExpired:
            outfile = "TIMEOUT"

    return outfile


def xdimacs(filename):
    return filename + DIMACS_SUFFIX


def parse_maxhs_output(filename):
    sol_found = False
    assigns = []
    time = -1.0
    memory = -1
    with open(filename, 'r') as file:
        for line in file.readlines():
            if line == "s OPTIMUM FOUND\n":
                sol_found = True
            if line[0] == 'v':
                assigns = [int(x) for x in line.split(' ')[1:]]
            if line.startswith("c CPU"):
                time = float(line.split(" ")[2])
            if line.startswith("c MEM MB"):
                memory = int(line.split(" ")[3])

        return {'solution': assigns, 'time': time, 'memory': memory}


def solve(filename, timeout=10000):
    dpts = []
    weights = []
    with open(filename, 'r') as fn:
        dpts = [int(x) for x in fn.readline().split(sep=' ')]
        num_dpts = len(dpts)
        weights = [[0 for x in range(num_dpts)] for y in range(num_dpts)]
        line = 1
        while True:
            line+=1
            ln = fn.readline()
            if ln == "" or ln == "\n":
                break
            constraint = [int(x) for x in ln.split(sep=' ')]
            if len(constraint) < 3:
                raise FileInputError(filename, ln, "incomplete constraint encountered at line %d" % line)
            x = dpts.index(constraint[0])
            y = dpts.index(constraint[1])
            w = constraint[2]

            def putweight(i, j, w):
                if weights[i][j] == 0:
                    weights[i][j] = w
                else:
                    raise FileInputError(filename, ln, "second constraint for existing pair (%d,%d) = %d at line %d"
                                         % (dpts[i], dpts[j], weights[i][j], line))
            # Matrix is triangular upper
            if x < y:
                putweight(x, y, w)
            else:
                putweight(y, x, w)

    ccs = CorrelationClusteringInstance(filename, dpts, weights)

    ccs.create_maxsat_instance()
    # Encode the problem in a max sat instance
    msat = MaxSATInstance(dpts, ccs.clauses)
    msat.print_to_file(xdimacs(filename))
    # Call MaxHS to solve the Max Sat problem
    mhs_out = maxhs(xdimacs(filename), timeout)
    # If MaxHS timed out
    if mhs_out == "TIMEOUT":
        ccs.timed_out = True
        return ccs
    # Parse the solution to find the assignments
    soln = parse_maxhs_output(mhs_out)
    ccs.solve_time = soln['time']
    ccs.solve_memory = soln['memory']
    start = time.time()
    for x in soln['solution']:
        wij = abs(x)
        i = int(wij / len(dpts))
        j = int(wij % len(dpts))
        if i < j:
            if x > 0:
                ccs.add_join((dpts[i], dpts[j]))
            else:
                ccs.add_diff((dpts[i], dpts[j]))
    ccs.cluster_time = time.time() - start
    return ccs


def main():
    if len(sys.argv) < 1:
        print("Usage:./correlation_clustering.py CORRELATIONS_FILE\n")
    filename = sys.argv[1]
    print(solve(filename))

if __name__ == "__main__":
    main()
