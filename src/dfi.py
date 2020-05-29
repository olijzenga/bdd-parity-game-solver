from dd.autoref import BDD
from parity_game import parity_game, sat_to_expr
import logging

def dfi(pg: parity_game):
    
    z = pg.bdd.add_expr('False')                    # No vertices are distractions
    f = { p : pg.bdd.false for p in pg.p.keys() }   # No vertices are frozen
    s = pg.bdd.false                                # Contains all edges of the winning strategy
    p = 0
    i = 0

    while p <= pg.d:

        logging.debug("Iteration " + str(i) + ":\n  Priority " + str(p) + "\n  Distractions: " + str([pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(z, care_vars=pg.variables)]))
        i += 1

        player = p % 2
        opponent = 1 - player
        v_p = pg.p[p]
        change = False

        for v in [ sat for sat in pg.bdd.pick_iter(v_p & ~z, care_vars=pg.variables)]:
            v_expr = pg.bdd.add_expr(sat_to_expr(v))
            (player_, move) = onestep(v, z, pg)
            # Remove previous strategies, and add new one (this would also work if move contains multiple vertices)
            s = (s & ~ v_expr)
            if move: s = s | (v_expr & pg.bdd.let(pg.substitution_list, move))
            if player_ != player:
                z = z | v_expr
                change = True
        
        if change:
            v = prio_lt(p, pg.p, pg) & f_none(f, pg)
            winning = (v & even(z, pg)) if player == 0 else (v & odd(z, pg))
            f[p] = f[p] | ~winning
            z = z & ~winning
            p = 0
        else:
            # forall v in V_<p: F[v]=p: F[v] <- -
            f[p] = f[p] & ~(prio_lt(p, pg.p, pg) & f[p])
            p += 1

    return even(z, pg), odd(z, pg), even(z, pg) & pg.even & s, odd(z, pg) & pg.odd & s

# Returns a bdd of all vertices which are not frozen
def f_none(f: dict, pg: parity_game):
    res = pg.bdd.true
    for p in f:
        res = res & ~f[p]
    return res

def winner(sat: dict, z: BDD, pg: parity_game):
    v = pg.bdd.add_expr(sat_to_expr(sat))
    return 0 if (v & even(z, pg)) == pg.bdd.true else 1

def onestep(v: dict, z: BDD, pg: parity_game):
    player = 0 if pg.bdd.quantify(pg.bdd.add_expr(sat_to_expr(v)) & pg.even, pg.variables, forall=False) == pg.bdd.true else 1
    if player == 0:
        succ = pg.bdd.add_expr(sat_to_expr(v)) & pg.e & pg.bdd.let(pg.substitution_list, even(z, pg))
    else:
        succ = pg.bdd.add_expr(sat_to_expr(v)) & pg.e & pg.bdd.let(pg.substitution_list, odd(z, pg))
    if pg.bdd.quantify(succ, (pg.variables + pg.variables_), forall=False) == pg.bdd.true:
        return player, succ

    return 1 - player, None

def onestep_0(z: BDD, pg: parity_game):
    # Edges which end in the winning area of Even
    e = even(z, pg)
    even_pre = preimage(e, pg)

    return ((pg.even & pg.bdd.quantify(even_pre, pg.variables, forall=False))
        | (pg.odd & pg.bdd.quantify(even_pre, pg.variables, forall=True)))

def onestep_1(z: BDD, pg: parity_game):
    # Edges which end in the winning area of Odd
    o = odd(z, pg)
    odd_pre = preimage(o, pg)

    res = (pg.even & ~(pg.bdd.quantify(odd_pre & pg.even, pg.variables, forall=False))
        | (pg.bdd.quantify(odd_pre & pg.odd, pg.variables, forall=False)))

    return res

def even(z: BDD, pg: parity_game):
    return (pg.prio_even & ~z) | (pg.prio_odd & z)

def odd(z: BDD, pg: parity_game):
    return (pg.prio_even & z) | (pg.prio_odd & ~z)

def preimage (v: BDD, pg: parity_game):
    v_next = pg.bdd.let(pg.substitution_list, v)
    return pg.bdd.quantify(v_next & pg.e, pg.variables_, forall = False)

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

    bdd = pg.bdd.add_expr('False')
    for current in sorted(p):
        if current >= prio:
            return bdd

        bdd = bdd | p[current]

    return bdd
