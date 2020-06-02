from dd.autoref import BDD
from parity_game import parity_game, sat_to_expr
import logging
import time

def fpj(pg: parity_game):
    
    z = pg.prio_even
    j = pg.bdd.false
    u = unjustified(j, pg)
    while unjustified(j, pg) != pg.bdd.false:   # Maybe there is a more efficient way of doing this?
        assert (u & j) == pg.bdd.false
        logging.debug("\n\n\nnext")
        logging.debug("J: " + pg.bdd_sat(pg.bdd.quantify(j, pg.variables_, forall=False)))
        logging.debug("U(J): " + pg.bdd_sat(u))
        z, j = next(z, j, pg)
        u = unjustified(j, pg)
    
    w0 = z
    w1 = pg.v & ~z
    s0 = j & pg.even & w0
    s1 = j & pg.odd & w1
    return w0, w1, s0, s1

def next(z: BDD, j: BDD, pg: parity_game):
    i = 0
    while (pg.p[i] & unjustified(j, pg)) == pg.bdd.false:
        i += 1
    logging.debug("prio: " + str(i))
    u = pg.bdd.quantify(pg.p[i] & ~j, pg.variables_, forall=False)

    logging.debug("U: " + pg.bdd_sat(u))
    logging.debug("Z: " + pg.bdd_sat(z))

    u_pd = xor(phi(z, pg), z) & u

    logging.debug("xor: " + pg.bdd_sat(xor(phi(z, pg), z)))
    logging.debug("phi: " + pg.bdd_sat(phi(z, pg)))
    logging.debug("U_pd: " + pg.bdd_sat(u_pd))

    if u_pd != pg.bdd.false:
        logging.debug("new")
        r = reaches(j, u_pd, pg)
        if i % 2 == 0:
            z_r = (z & ~(r & pg.prio_odd)) & prio_lt(i, pg.p, pg)
        else:
            z_r = (z | (r & pg.prio_even)) & prio_lt(i, pg.p, pg)
        j_t = j & ~(r & pg.bdd.let(pg.substitution_list, pg.v))
        j_ = j_t | strategy_0(z, u_pd, pg)
        z_ = (z & prio_gt(i, pg.p, pg)) | (xor(z, u_pd) | z_r)
    else:
        logging.debug("no new")
        strat = strategy_0(z, u, pg)
        logging.debug("new moves: " + str([ pg.sat_to_hex(sat) + " <==> " + pg.sat_to_hex(sat, edge=True) for sat in pg.bdd.pick_iter(strat, care_vars=(pg.variables_ + pg.variables))]))
        j_ = j | strat
        z_ = z
    
    return z_, j_

def strategy_0(z: BDD, u: BDD, pg: parity_game):
    j = pg.bdd.false

    even = pg.even & z
    odd = pg.odd & ~z
    losing = pg.v & ~(even | odd) # vertices won by the player that does not own it

    z_ = pg.bdd.let(pg.substitution_list, z)

    j = j | (pg.e & even & z_ & u)
    j = j | (pg.e & odd & ~z_ & u)
    j = j | (pg.e & losing & u)

    return j
##{v ∈ V0|∃w:(v, w) ∈ E ∧ w ∈ S } ∪ { v ∈ V1| ∀w: (v, w) ∈ E ⇒ w∈S}
def phi(z: BDD, pg: parity_game):

    z_ = pg.bdd.let(pg.substitution_list, z)

    res = ((pg.even & pg.bdd.quantify(pg.e & z_, pg.variables_, forall=False))
        | (pg.odd & pg.bdd.quantify(pg.bdd.add_expr('{a} => {b}'.format(a=pg.e, b=z_)), pg.variables_, forall=True)))
    return res

def preimage(v: BDD, pg: parity_game):
    v_next = pg.bdd.let(pg.substitution_list, v)
    return pg.bdd.quantify(v_next & pg.e, pg.variables_, forall = False)

def xor(a: BDD, b: BDD):
    return (a & ~b) | (~a & b)

def unjustified(j: BDD, pg: parity_game):
    return pg.v & ~pg.bdd.quantify(j, pg.variables_, forall=False)

# Set of vertices from which x can be reached over edges in j
def reaches(j: BDD, x: BDD, pg: parity_game):
    # Preimage of v using edges in e
    def preimage(v: BDD, e: BDD):
        v_next = pg.bdd.let(pg.substitution_list, v)
        return pg.bdd.quantify(v_next & e, pg.variables_, forall = False)

    pre = x | preimage(x, j)
    pre_ = preimage(pre, j)
    while (pre_ & ~pre) != pg.bdd.false:
        pre = pre | pre_
        pre_ = preimage(pre_, j)

    return pre

def prio_lt(prio: int, p: dict, pg: parity_game):
    """Returns a BDD representing all vertices with priority lower than _prio_

    :param prio: all selected vertices should have lower priority than prio
    :type prio: int
    :param p: dictionary containing BDD's for vertices of each priority
    :type p: dict
    :param pg: parity game instance
    :type pg: parity_game
    :return: bdd of all vertices with priority lower than or equal to prio
    :rtype: BDD
    """

    bdd = pg.bdd.false
    for current in p.keys():
        if current < prio:
            bdd = bdd | p[current]

    return bdd

def prio_gt(prio: int, p: dict, pg: parity_game):
    bdd = pg.bdd.false
    for current in p.keys():
        if current > prio:
            bdd = bdd | p[current]
    
    return bdd