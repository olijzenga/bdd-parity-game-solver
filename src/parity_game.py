from dd.cudd import BDD
from bdd_provider import make_bdd
from graphviz import Source

class parity_game:

    def __init__ (self, bdd: BDD, variables, variables_, v: BDD, e: BDD, even: BDD, odd: BDD, p):
        """Initializes a parity game instance

        :param bdd: the BDD used as the data structure for this parity game
        :type bdd: dd.autoref.BDD
        :param variables: variables used for representing vertices in BDDs
        :type variables: list<str>
        :param variables_: variables used to represent successor vertices for edges and strategies
        :type variables_: list<str>
        :param v: BDD which can determine whether a vector represents a vertex in the parity game
        :type v: dd.autoref.BDD
        :param e: BDD which represents the edges of the parity game
        :type e: dd.autoref.BDD
        :param even: BDD which determines whether a vertex is owned by player even
        :type even: dd.autoref.BDD
        :param odd: BDD which determines whether a vertex is owned by player odd
        :type odd: dd.autoref.BDD
        :param p: maps a priority to a BDD which determines if a vertex has that priority
        :type p: dict<dd.autoref.BDD>
        """
        self.bdd = bdd
        self.variables = variables
        self.variables_ = variables_
        self.substitution_list = { variables[i] : variables_[i] for i in range(len(variables)) }
        self.reverse_substitution_list = { variables_[i] : variables[i] for i in range(len(variables)) }
        self.v = v
        self.e = e
        self.even = even
        self.odd = odd
        self.p = p
        self.d = max(p)

        self.prio_even = bdd.false
        self.prio_odd = bdd.false

        # Build a BDD for deciding 
        for prio in p:
            if prio % 2:
                self.prio_odd = self.prio_odd | p[prio]
            else:
                self.prio_even = self.prio_even | p[prio]

        # Add empty priority BDDs for priorities which have no vertices
        for prio in range(0, self.d):
            if prio not in p:
                p[prio] = bdd.false

    # Convert a SAT value to a hex string for more compact representaton
    def sat_to_hex(self, sat, edge=False):
        res = ""

        bytea = []
        pos = 0
        cur = 0
        for var in self.variables:
            if(sat[var]):
                cur += pow(2,pos)
            if pos == 7:
                bytea.append(cur)
                cur = 0
                pos = 0
            else:
                pos += 1
        if pos != 0:
            bytea.append(cur)

        bytea.reverse()
        res += ''.join('{:02x}'.format(x) for x in bytea)

        if edge:
            bytea = []
            pos = 0
            cur = 0
            for var in self.variables_:
                if(sat[var]):
                    cur += pow(2,pos)
                if pos == 7:
                    bytea.append(cur)
                    cur = 0
                    pos = 0
                else:
                    pos += 1
            if pos != 0:
                bytea.append(cur)

            bytea.reverse()
            res = ''.join('{:02x}'.format(x) for x in bytea)

        return res

    def show(self):
        self.make_dot("output/pg.dot")
        with open("output/pg.dot", "r") as text_file:
            s = Source(text_file.read(), filename="output/dot.png", format="png")
            s.view()

    def bdd_sat(self, bdd: BDD):
        return ', '.join([self.sat_to_hex(sat) for sat in self.bdd.pick_iter(bdd, self.variables)])

    def bdd_sat_edges(self, bdd: BDD):
        return ', '.join([self.sat_to_hex(sat) + " <==> " + self.sat_to_hex(sat, edge=True) for sat in self.bdd.pick_iter(bdd, care_vars=(self.variables_ + self.variables))])

    # Gather data used for exporting this parity game to a dot file, or printing it
    def get_repr_data(self):
        data = {}

        for v_0 in self.bdd.pick_iter(self.even, care_vars=self.variables):
            data[self.sat_to_hex(v_0)] = ('Even', None, [])
        for v_1 in self.bdd.pick_iter(self.odd, care_vars=self.variables):
            data[self.sat_to_hex(v_1)] = ('Odd ', None, [])
        for prio in self.p:
            for v in self.bdd.pick_iter(self.p[prio], care_vars=self.variables):
                d = data[self.sat_to_hex(v)]
                data[self.sat_to_hex(v)] = (d[0], prio, [])
        for e in self.bdd.pick_iter(self.e, care_vars=(self.variables + self.variables_)):
            d = data[self.sat_to_hex(e)]
            d[2].append(self.sat_to_hex(e, edge=True))
            data[self.sat_to_hex(e)] = (d[0], d[1], d[2])

        return data

    def __repr__(self):
        
        data = self.get_repr_data()

        res = ""
        for h in sorted(data):
            d = data[h]
            res += h + ' ' + d[0] + ' prio: ' + str(d[1]) + ' edges: ' + (', '.join(d[2])) + '\n'

        return res

    def make_dot(self, filename):
        
        data = self.get_repr_data()

        res = "digraph parity_game {\n"
        for h in sorted(data):
            d = data[h]
            res += "\t\"" + h + "\" [label=\"" + str(d[1]) + " (" + h + ")\", shape=" + ('diamond' if d[0] == 'Even' else 'box') + "];\n"

        for h in sorted(data):
            d = data[h]
            #for e in d[2]:
            #    res += "\t\"" + h + "\" -> \"" + e + "\"\n"
            res += "\t\"" + h + "\" -> {" + (', '.join([ "\"" + x + "\"" for x in d[2] ])) + "};\n"

        res += "\n}"

        with open(filename, "w") as text_file:
            print(res, file=text_file)

    def copy(self, deep=False):
        if deep:
            bdd = make_bdd()
            bdd.declare(*self.variables)
            bdd.declare(*self.variables_)
            v = self.bdd.copy(self.v, bdd)
            e = self.bdd.copy(self.e, bdd)
            even = self.bdd.copy(self.even, bdd)
            odd = self.bdd.copy(self.odd, bdd)
            p = { prio : self.bdd.copy(self.p[prio], bdd) for prio in self.p.keys() }
            c = parity_game(bdd, self.variables, self.variables_, v, e, even, odd, p)
        else:
            c = parity_game(self.bdd, self.variables, self.variables_, self.v, self.e, self.even, self.odd, self.p)
        return c

    def has_successor (self, U):
        #check whether U = { u in V | u in U /\ exists v in V: u --> v } 
        V_= self.bdd.let(self.substitution_list, self.v)
        U_next = self.bdd.let(self.substitution_list, U)
        Z = self.bdd.quantify(U_next & self.e, self.variables_, forall = False) & U
        return (Z == U)
        
    def successor (self, U):
        U_next = self.bdd.quantify(self.e & U, self.variables, forall = False)
        U_next = U | self.bdd.let(self.reverse_substitution_list, U_next)
        return U_next

    def reachable (self, U):
        U_next = self.successor(U)
        i = 0
        while U != U_next:
            U = U_next
            U_next = self.successor(U)
            i = i +1
        return U_next

    def predecessor (self, player, U):
        # U is a BDD representing a set of vertices
        # player is either string 'even' or string 'odd'
        (V_player,V_opponent) = (self.even, self.odd) if (player == 'even') else (self.odd, self.even)
        V_ = self.bdd.let(self.substitution_list, self.v)
        U_next = self.bdd.let(self.substitution_list, U)
        U_player = V_player & self.bdd.quantify(U_next & self.e, self.variables_, forall = False)
        # V_opponent /\ {v in V | forall u in V: v --> u ==> u in U } = 
        # V_opponent /\ {v in V | ~ (exists u in V: v --> u /\ u in V\U) } 
        U_opponent =  V_opponent & ~(self.bdd.quantify(self.e & V_ & ~U_next, self.variables_, forall = False) )
        # return union of the two sets
        return U_player | U_opponent
    
    def predecessor_gen (self, player, X, U):
        # X,U are BDDs representing a set of vertices
        # X is used to restrict the set of edges to stay within X
        # player is either string 'even' or string 'odd'
        (V_player,V_opponent) = (self.even, self.odd) if (player == 'even') else (self.odd, self.even)
        V_ = self.bdd.let(self.substitution_list, self.v)
        X_ = self.bdd.let(self.substitution_list, X)
        E  = self.e & X & X_
        U_next = self.bdd.let(self.substitution_list, U)
        U_player = V_player & self.bdd.quantify(U_next & E, self.variables_, forall = False)
        # V_opponent /\ {v in V | forall u in V: v --> u ==> u in U } = 
        # V_opponent /\ {v in V | ~ (exists u in V: v --> u /\ u in V\U) } 
        U_opponent =  V_opponent & ~(self.bdd.quantify(E & V_ & ~U_next, self.variables_, forall = False) )
        # return union of the two sets
        return U_player | U_opponent
    
    
    def attractor (self, player, A):
        # U is a BDD representing a set of vertices
        # player is either string 'even' or string 'odd'
        # attractor computation is a least fixpoint computation
        tmp = self.bdd.false
        tmp_= A
        while tmp != tmp_:
            tmp = tmp_
            tmp_ = tmp_ | self.predecessor ( player, tmp_)
        return tmp

    def attractor_gen(self, player, V, A):
        tmp = self.bdd.false
        tmp_ = A & V
        while tmp != tmp_:
            tmp = tmp_
            tmp_ = V & (tmp_ | self.predecessor_gen( player, V, tmp_))    # the use of predecessor_gen and intersection with V are both required!
        return tmp

    def remove (self, A):
        # removing a set of vertices represented by BDD A 
        (self.v, self.even, self.odd) = (self.v & ~A, self.even & ~A, self.odd & ~A)
        A_ = self.bdd.let(self.substitution_list, A)
        self.e = self.e & ~A & ~A_
        p_ = { i : self.p[i] & ~A for i in self.p if self.p[i] & ~A != self.bdd.false}
        self.p = p_
        #self.bdd.collect_garbage()

# Convert a variable assignment to a boolean expression
def sat_to_expr(sat: dict):
    return '&'.join([ var if sat[var] else ('~' + var) for var in sat.keys() ])