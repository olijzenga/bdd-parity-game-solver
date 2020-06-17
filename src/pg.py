import networkx as nx
import numpy as np
import math
import re
import sys
from parity_game import parity_game
from bdd_provider import make_bdd

class ParityGame(object):
    def __init__(self, nodecountOrParityGame, graph=None):
        if type(nodecountOrParityGame) == int:
            # Initializes an empty parity game with nodecount nodes
            nodecount = nodecountOrParityGame
            self.graph = nx.empty_graph(nodecount, None, nx.DiGraph)  # directed graph
            self.owner = np.zeros(nodecount, dtype=np.int8)
            self.priority = np.zeros(nodecount, dtype=np.int32)
            self.label = np.zeros(nodecount, dtype=np.object_)
        else:
            # Deep copies the given graph
            originalPG = nodecountOrParityGame
            self.graph = nx.DiGraph(graph)
            self.owner = originalPG.owner.copy()
            self.priority = originalPG.priority.copy()
            self.label = originalPG.label.copy()

    def set_node(self, node, owner, priority, label):
        """Sets information of a specific node."""
        self.owner[node] = owner
        self.priority[node] = priority
        self.label[node] = label

    def add_edge(self, src, tgt):
        self.graph.add_edge(src, tgt)

    def priorities(self):
        return self.priority.copy()

    def maxPriority(self):
        """Returns the maximum priority in the parity game"""
        return max(self.priority[n] for n in self.graph.nodes())

    def nodesWithPriority(self, p):
        """Returns a list of nodes with priority p"""
        return [n for n in self.graph.nodes() if self.priority[n] == p]

    def numNodes(self):
        """Returns the number of nodes in the graph"""
        return len(self.graph)

    def nodes(self):
        """Returns a list of nodes in the graph"""
        return self.graph.nodes()

    def edges(self):
        return [e for e in self.graph.edges]

    def getOwner(self, n):
        """Returns the owner of node n"""
        return self.owner[n]

    def getPriority(self, n):
        """Given an iterable containing nodes, returns a list of priorities of the nodes. Given a node n, returns its priority."""
        try:
            return [self.priority[nPrime] for nPrime in n]
        except TypeError as e:
            return self.priority[n]

    def hasEdge(self, u, v):
        """Checks if there is an edge from u to v"""
        return self.graph.has_edge(u, v)

    def withoutNodes(self, U):
        """Returns a parity game identical to self, but without the nodes in U"""
        # Invert nodes
        V = [n for n in self.graph.nodes() if n not in U]
        return self.withNodes(V)

    def withNodes(self, U):
        """Returns a parity game identical to self, but with only the nodes U"""
        graph = self.graph.subgraph(U)
        return ParityGame(self, graph)

    def getSuccessors(self, n):
        """Returns the succesors of n or in a list every successor for every node in n."""
        try:
            return [item for sublist in [self.graph.successors(nPrime) for nPrime in n]
                         for item in sublist]
        except TypeError as e:
            return self.graph.successors(n)

    def numSuccessors(self, n):
        return self.graph.out_degree(n)

    def invert(self):
        """Returns the mirrored parity game where even is odd, and odd is even"""
        H = self.withNodes(self.nodes())

        for i in range(len(H.priority)):
            H.priority[i] += 1

        for i in range(len(H.owner)):
            H.owner[i] = (H.owner[i] + 1) % 2

        return H

def read_parity_game(path, verbose=False):
    """Read a parity game from a file.
    If the file does not exist, assumes the path is a parity game.
    """

    try:
        with open(path, 'r') as f:
            txt = f.read()
    except Exception as e:
        raise e

    f = (s for s in txt.split("\n"))

    m = re.match('parity\W+(\d+)', next(f))
    assert(m)  # must start with line: "parity <number of nodes>;"

    # initialize game graph with <number of nodes> of header line
    # node ids are 0 .. <number of nodes>
    g = ParityGame(int(m.group(1)))

    # compile the pattern for each line
    # <node id> <priority> <owner> <successorlist> <label>
    # successor list is a comma-separated list of successors
    # label can optionally be quoted with ""
    patt = re.compile('(\d+)\W+(\d+)\W+(\d+)\W+((?:\d+[, ]*)+)(.*);')

    # read every line
    for line in f:
        m = re.match(patt, line)
        if m:
            node = int(m.group(1))
            priority = int(m.group(2))
            owner = int(m.group(3))
            succ = map(int, re.findall('\d+', m.group(4)))
            label = m.group(5)
            if len(label) > 0 and label[0] == '"':
                label = label[1:-1]  # remove quotes
            g.set_node(node, owner, priority, label)
            for tgt in succ:
                g.add_edge(node, tgt)
        elif verbose:
            print("bad line: " + line)

    return g

def acquire_parity_game():
    """Reads a parity game from a file indicated by the first command line argument passed, or from stdin"""
    if len(sys.argv) > 1:
        G = read_parity_game(sys.argv[1])
    else:
        G = read_parity_game(sys.stdin.read())
    return G

def oink_to_sym(pg: ParityGame):
    
    bdd = make_bdd()
    nodecount = len(pg.graph)
    size = math.ceil(math.log(nodecount, 2))

    variables = [ "x" + str(x) for x in range(size) ]
    variables_ = [ "x" + str(x) + "_" for x in range(size) ]

    bdd.declare(*variables)
    bdd.declare(*variables_)

    def v_to_expr(v: int, successor=False):
        binary = [ bool(v & (1<<n)) for n in range(size) ]
        s = ""
        for i in range(len(binary)):
            if binary[i]:
                if successor:
                    s += "&" + variables_[i]
                else:
                    s += "&" + variables[i]
            else:
                if successor:
                    s += "&~" + variables_[i]
                else:
                    s += "&~" + variables[i]
        return s[1:]

    # Declare vertices
    if math.log(nodecount, 2) != size:
        raise Exception("Node count other than 2^x currently not supported")
    else:
        v = bdd.true

    # Declare edges
    e = bdd.false
    for edge in pg.edges():
        s = v_to_expr(edge[0]) + "&" + v_to_expr(edge[1], successor=True)
        e = e | bdd.add_expr(s)

    # Declare priorities
    priorities = pg.priorities()
    p = { prio : bdd.false for prio in range(max(priorities) + 1) }
    even = bdd.false
    odd = bdd.false

    for i in range(nodecount):
        # Set priority
        expr = bdd.add_expr(v_to_expr(i))
        prio = int(priorities[i])

        p[prio] = p[prio] | expr

        # Set owner
        if pg.getOwner(i) == 0:
            even = even | expr
        else:
            odd = odd | expr

    return parity_game(bdd, variables, variables_, v, e, even, odd, p)
    