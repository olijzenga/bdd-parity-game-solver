from dd.autoref import BDD
from parity_game import parity_game, sat_to_expr
import logging

def fpj(pg: parity_game):
    
    z = pg.prio_even
    j = pg.bdd.false

    while (j != pg.v):   # Maybe there is a more efficient way of doing this?
        z, j = next(z, j, pg)
    
    return z, j

def next(z: BDD, j: BDD, pg: parity_game):
    i = 0
    while (pg.p[i] & ~j) == False:
        i += 1
    u = pg.p[i] & ~j
    u_pd = xor(phi(z, pg), z, pg) & u

    if u_pd != pg.bdd.false:
        r = reaches(j, u_pd, pg)
        if i % 2 == 0:
            z_r = (z & ~(r & pg.prio_odd)) & prio_lt(i, pg.p, pg)
        else:
            z_r = (z | (r & pg.prio_even)) & prio_lt(i, pg.p, pg)
        j_t = j & ~(r & pg.bdd.let(pg.substitution_list, pg.v))
        j_ = j_t | strategy_0(z, u_pd, pg)
        z_ = (z & prio_gt(i, pg.p, pg)) | (xor(z, u_pd, pg) | z_r)
    else:
        j_ = j | strategy_0(z, u, pg)
        z_ = z
    
    return z_, j_

def strategy_0(z: BDD, u: BDD, pg: parity_game):
    j = pg.bdd.false

    even = pg.even & z
    odd = pg.odd & ~z
    losing = pg.v & ~(even | odd) # vertices won by the player that does not own it

    z_ = pg.bdd.let(pg.substitution_list, z)

    j = j | (pg.e & even & z_)
    j = j | (pg.e & odd & ~z_)
    j = j | (pg.e & losing)

    return j
##{v ∈ V0|∃w:(v, w) ∈ E ∧ w ∈ S } ∪ { v ∈ V1| ∀w: (v, w) ∈ E ⇒ w∈S}
def phi(z: BDD, pg: parity_game):
    z_ = pg.bdd.let(pg.substitution_list, z)

    return ((pg.even & pg.bdd.quantify(pg.e & z_, pg.variables_, forall=False))
        | (pg.odd & pg.bdd.quantify(pg.bdd.let({ 'a': pg.e, 'b': z_}, pg.bdd.add_expr('a => b')), pg.variables_, forall=True)))

def preimage (v: BDD, pg: parity_game):
    v_next = pg.bdd.let(pg.substitution_list, v)
    return pg.bdd.quantify(v_next & pg.e, pg.variables_, forall = False)

def xor(a: BDD, b: BDD, pg: parity_game):
    return pg.bdd.add_expr((a | b) & ~(a | b))

def reaches(j: BDD, u_pd: BDD, pg: parity_game):
    return u_pd

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