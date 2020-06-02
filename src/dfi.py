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

        logging.debug(
            "Iteration " + str(i) + 
            ":\n  Priority " + str(p) + 
            "\n  Distractions: " + str([pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(z, care_vars=pg.variables)]) +
            "\n  Frozen vertices:\n    " + str('\n    '.join([ str(p) + ': ' + str([ pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(f[p], care_vars=pg.variables)]) for p in f.keys() ]))
        )
        i += 1

        player = p % 2
        v_p = pg.p[p]
        v = (v_p & ~z)

        os = onestep_0(v, z, pg)
        if player == 0:
            z_ = v & ~os
        else:
            z_ = os
        logging.debug("z_: " + pg.bdd_sat(z_))
        change = z_ != pg.bdd.false
        z = z | z_
        # Update strategy
        s = s & ~v
        s = s | (v & pg.even & pg.e & pg.bdd.let(pg.substitution_list, even(z, pg)))
        s = s | (v & pg.odd & pg.e & pg.bdd.let(pg.substitution_list, odd(z, pg)))
        
        if change:
            v = prio_lt(p, pg.p, pg) & f_none(f, pg)
            logging.debug("non-frozen vertices with prio lower than {0}: {1}".format(p, pg.bdd_sat(v)))
            winning = (v & even(z, pg)) if player == 0 else (v & odd(z, pg))
            f[p] = (v & ~winning) | f[p]
            z = (~winning) & z
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

# def onestep(v: dict, z: BDD, pg: parity_game):
#     player = 0 if pg.bdd.quantify(pg.bdd.add_expr(sat_to_expr(v)) & pg.even, pg.variables, forall=False) == pg.bdd.true else 1
#     if player == 0:
#         succ = pg.bdd.add_expr(sat_to_expr(v)) & pg.e & pg.bdd.let(pg.substitution_list, even(z, pg))
#     else:
#         succ = pg.bdd.add_expr(sat_to_expr(v)) & pg.e & pg.bdd.let(pg.substitution_list, odd(z, pg))
#     if pg.bdd.quantify(succ, (pg.variables + pg.variables_), forall=False) == pg.bdd.true:
#         return player, succ

#     return 1 - player, None

# def onestep_0(v: BDD, z: BDD, pg: parity_game):
#     # Edges which end in the winning area of Even
#     e = even(z, pg)
#     even_pre = preimage(e, pg)

#     return ((v & pg.even & pg.bdd.quantify(even_pre, pg.variables, forall=False))
#         | (v & pg.bdd.quantify(pg.odd & even_pre, pg.variables, forall=True)))

def onestep_0(v: BDD, z: BDD, pg: parity_game):

    z_ = pg.bdd.let(pg.substitution_list, even(z, pg))

    res = ((pg.even & pg.bdd.quantify(pg.e & z_, pg.variables_, forall=False))
        | (pg.bdd.quantify(pg.odd & pg.bdd.add_expr('{a} => {b}'.format(a=pg.e, b=z_)), pg.variables_, forall=True)))
    return v & res

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
    for current in p.keys():
        if current < prio:
            bdd = bdd | p[current]
            logging.debug("prio " + str(current))

    return bdd
