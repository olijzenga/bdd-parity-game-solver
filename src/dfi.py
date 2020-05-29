from dd.autoref import BDD
from parity_game import parity_game

def dfi_no_freeze(pg: parity_game):
    
    z = pg.bdd.add_expr('False')        # No vertices are distractions
    p = 0
    i = 0

    while p <= pg.d:

        print("Iteration " + str(i) + ":\n  Priority " + str(p) + "\n  Distractions: " + str([sat for sat in pg.bdd.pick_iter(z)]))
        i += 1

        player = p % 2
        opponent = 1 - player
        v_p = pg.p[p]
        v = v_p & ~z
        new_distractions = v & onestep(opponent, z, pg)
        new_distractions_sat = [ sat for sat in pg.bdd.pick_iter(new_distractions) ]
        print("  New distractions: " + str(new_distractions_sat))
        
        if new_distractions_sat:
            z = (z | new_distractions) & ~(prio_lt(p, pg.p, pg))
            p = 0
        else:
            p += 1

    w_0 = (pg.even & ~z) | (pg.odd & z)
    return w_0, (pg.v & ~w_0)

def onestep(player: int, z: BDD, pg: parity_game):
    if(player == 0):
        return onestep_0(z, pg)
    else:
        return onestep_1(z, pg)

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

    print("Odd: {0}".format(pg.bdd_sat(o)))
    print("preimage(odd(z)): {0}".format(pg.bdd_sat(odd_pre)))

    res = (pg.even & ~(pg.bdd.quantify(odd_pre & pg.even, pg.variables, forall=False))
        | (pg.bdd.quantify(odd_pre & pg.odd, pg.variables, forall=False)))

    print("Res: {0}".format(pg.bdd_sat(res)))

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
