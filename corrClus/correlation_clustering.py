import sys
import subprocess


class MaxSATInstanceException(Exception):
    def __init__(self, msg):
        self.message = msg


class MaxSATInstance(object):
    def __init__(self, pvars, clauses):
        self.vars = vars
        self.clauses = clauses
        self.top = 263 # Always pick this as the top weight
        self.nbvar = len(pvars)
        self.nbclauses = len(clauses)

        # Check weights
        sumw = 0
        maxw = 0
        for c in clauses:
            w = c[0]
            if w < 1:
                raise MaxSATInstanceException("Instance with weight < 1")
            sumw += w
            maxw = max(w, maxw)

        if sumw >= 263:
            raise MaxSATInstanceException("Instance with sum weights > 263")

    def print_to_file(self, filename):
        with open(filename, 'w') as outf:
            print("p wcnf %d %d %d" % (self.nbvar, self.nbclauses, self.top), file=outf)

            for ic, clause in enumerate(self.clauses):
                weight = clause[0]
                # if it's a hard clause
                if weight <= 0:
                    weight = self.top
                print("%d %s 0" % (weight, ' '.join([refng(self.vars, i) for i in clause[1]])), file=outf)


class CorrelationClusteringInstance(object):

    def __init__(self, data_points, weights):
        self.data_points = data_points
        self.weights = weights
        self.clusters = []

    def pair_lit(self, i, j):
        return i * len(self.data_points) + j

    def create_maxsat_instance(self):
        clauses = []
        idx = -
        # Add all the weight-clauses wij
        for iw, wline in enumerate(self.weights):
            for i, w in enumerate(wline):
                if __name__ == '__main__':
                    if w > 0:
                        wij = self.pair_lit(iw, i)
                        clauses.append((w, [wij]))
                        idx += 1
            # Encode cluster constraint.
            # If pairs ij, ik, then jk

    def __str__(self):
        if len(self.data_points) < 20:
            return ("%d data points:\n%s\nWeights:\n%s\n\n%d clusters:\n%s" %
                    (len(self.data_points),
                     " ".join([str(x) for x in self.data_points]),
                     "\n".join([' '.join([pnz(i) for i in x]) for x in self.weights]),
                     len(self.clusters),
                     " ".join(self.clusters)))
        else:
            return "%d data points, %d clusters found." % (len(self.data_points), len(self.clusters))


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

def refng(a,i):
    if i < 0:
        return -a[-i]
    else:
        return a[i]


def minisat(enc):
    subprocess.call(["../minisat", enc['name'], enc['name'] + ".res"])


def main():
    if len(sys.argv) < 1:
        print("Usage:./correlation_clustering.py CORRELATIONS_FILE\n")
    filename = sys.argv[1]
    num_dpts = 0
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
            if ln == "":
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
                putweight(x,y,w)
            else:
                putweight(y,x,w)

    ccs = CorrelationClusteringInstance(dpts, weights)

    print(ccs)


if __name__ == "__main__":
    main()
