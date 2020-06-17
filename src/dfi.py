from dd.autoref import BDD
from parity_game import parity_game, sat_to_expr
import logging

logger = logging.getLogger(__name__)
debug = logger.isEnabledFor(logging.DEBUG)

#@profile
def dfi(pg: parity_game, strategy=True):
    
    z = pg.bdd.false                                # No vertices are distractions
    f = { p : pg.bdd.false for p in pg.p.keys() }   # No vertices are frozen
    s = pg.bdd.false                                # Contains all edges of the winning strategy
    p = 0                                           # Current priority
    i = 0                                           # Iteration count for debugging

    while p <= pg.d:

        if debug:
            logger.debug(
                "Iteration " + str(i) + 
                ":\n  Priority " + str(p) + 
                "\n  Distractions: " + str([pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(z, care_vars=pg.variables)]) +
                "\n  Frozen vertices:\n    " + str('\n    '.join([ str(p) + ': ' + str([ pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(f[p], care_vars=pg.variables)]) for p in f.keys() ]))
            )
            i += 1
     
        player = p % 2
        v_p = pg.p[p]
        # v = (v_p & ~z) & f_none(f, pg)
        # This re-ordering improves performance
        v = v_p & ~z
        for i in range(p, pg.d + 1):
            v = v & ~f[i]

        os = onestep_0(v, z, pg)
        if player == 0:
            z_ = v & ~os
        else:
            z_ = os

        z = z | z_
        # Update strategy
        if strategy:
            s = s & ~v
            s = s | (v & pg.even & pg.e & pg.bdd.let(pg.substitution_list, even(z, pg)))
            s = s | (v & pg.odd & pg.e & pg.bdd.let(pg.substitution_list, odd(z, pg)))

        if debug:
            logger.debug("z_: " + pg.bdd_sat(z_))
        
        if z_ != pg.bdd.false:
            v = prio_lt(p, pg.p, pg) & f_none(f, pg)
            # This reordering improves performance
            # v = prio_lt(p, pg.p, pg)
            # for i in range(pg.d + 1):
            #     v = v & ~f[i]
            winning = (v & even(z, pg)) if player == 0 else (v & odd(z, pg))
            f[p] = (v & ~winning) | f[p]
            z = (~winning) & z
            p = 0

            if debug:
                logger.debug("non-frozen vertices with prio lower than {0}: {1}".format(p, pg.bdd_sat(v)))

        else:
            # forall v in V_<p: F[v]=p: F[v] <- -
            f[p] = f[p] & ~prio_lt(p, pg.p, pg)
            # for i in range(p):
            #     f[p] = f[p] & ~pg.p[i]
            p += 1

    if strategy:
        return even(z, pg), odd(z, pg), even(z, pg) & pg.even & s, odd(z, pg) & pg.odd & s
    else:
        return even(z, pg), odd(z, pg)

#@profile
def dfi_no_freezing(pg: parity_game, strategy=True):
    
    z = pg.bdd.false                                # No vertices are distractions
    s = pg.bdd.false                                # Contains all edges of the winning strategy
    p = 0                                           # Current priority
    i = 0                                           # Iteration count for debugging

    while p <= pg.d:

        if debug:
            logger.debug(
                "Iteration " + str(i) + 
                ":\n  Priority " + str(p) + 
                "\n  Distractions: " + str([pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(z, care_vars=pg.variables)])
            )
            i += 1
     
        player = p % 2
        v_p = pg.p[p]
        #v = (v_p & ~z) & f_none(f, pg)
        # This re-ordering improves performance
        v = v_p & ~z

        os = onestep_0(v, z, pg)
        if player == 0:
            z_ = v & ~os
        else:
            z_ = os

        z = z | z_
        # Update strategy
        if strategy:
            s = s & ~v
            s = s | (v & pg.even & pg.e & pg.bdd.let(pg.substitution_list, even(z, pg)))
            s = s | (v & pg.odd & pg.e & pg.bdd.let(pg.substitution_list, odd(z, pg)))

        if debug:
            logger.debug("z_: " + pg.bdd_sat(z_))
        
        if z_ != pg.bdd.false:
            z = z & ~prio_lt(p, pg.p, pg)
            p = 0

            if debug:
                logger.debug("non-frozen vertices with prio lower than {0}: {1}".format(p, pg.bdd_sat(v)))

        else:
            p += 1

    if strategy:
        return even(z, pg), odd(z, pg), even(z, pg) & pg.even & s, odd(z, pg) & pg.odd & s
    else:
        return even(z, pg), odd(z, pg)

# Returns a bdd of all vertices which are not frozen
def f_none(f: dict, pg: parity_game):
    res = pg.bdd.true
    for p in f:
        res = res & ~f[p]
    return res

#@profile
def onestep_0(v: BDD, z: BDD, pg: parity_game):

    z_ = pg.bdd.let(pg.substitution_list, even(z, pg))

    res = ((pg.even & pg.bdd.quantify(pg.e & z_, pg.variables_, forall=False))
        | (pg.bdd.quantify(pg.odd & (~(pg.e) | z_), pg.variables_, forall=True)))
    return v & res

#@profile
def even(z: BDD, pg: parity_game):
    return (pg.prio_even & ~z) | (pg.prio_odd & z)

#@profile
def odd(z: BDD, pg: parity_game):
    return (pg.prio_even & z) | (pg.prio_odd & ~z)

#@profile
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
            
            if debug:
                logger.debug("prio " + str(current))

    return bdd
