from dd.autoref import BDD
from parity_game import parity_game, sat_to_expr
import logging
import time

logger = logging.getLogger(__name__)
debug = logger.isEnabledFor(logging.DEBUG)

#@profile
def fpj(pg: parity_game):
    """Symbolic implementation of the FPJ algorithm

    :param pg: parity game instance
    :type pg: parity_game
    :return: BDD representing the set of vertices won by either players, and their winning strategy
    :rtype: (BDD, BDD, BDD, BDD)
    """
    
    z = pg.prio_even
    j = pg.bdd.false
    u = unjustified(j, pg)
    while u != pg.bdd.false:

        if debug:
            logging.debug("\n\n\nnext")
            logging.debug("J: " + pg.bdd_sat(pg.bdd.quantify(j, pg.variables_, forall=False)))
            logging.debug("U(J): " + pg.bdd_sat(u))

        z, j = next(z, j, u, pg)
        u = unjustified(j, pg)
    
    w0 = z
    w1 = pg.v & ~z
    s0 = j & pg.even & w0
    s1 = j & pg.odd & w1
    return w0, w1, s0, s1

#@profile
def next(z: BDD, j: BDD, u: BDD, pg: parity_game):
    """A monotonic iteration of the FPJ algorithm

    :param z: BDD representing vertices estimated to be won by Even
    :type z: BDD
    :param j: BDD representing the justification graph
    :type j: BDD
    :param u: BDD representing the set of currently unjustified vertices
    :type u: BDD
    :param pg: parity game instance
    :type pg: parity_game
    :return: BDDs representing updated Z and J
    :rtype: (BDD, BDD)
    """
    i = 0
    while (pg.p[i] & u) == pg.bdd.false:
        i += 1
    u = pg.p[i] & u

    if debug:
        logging.debug("prio: " + str(i))
        logging.debug("U: " + pg.bdd_sat(u))
        logging.debug("Z: " + pg.bdd_sat(z))

    u_pd = xor(phi(z, pg), z) & u

    if debug:
        logging.debug("xor: " + pg.bdd_sat(xor(phi(z, pg), z)))
        logging.debug("phi: " + pg.bdd_sat(phi(z, pg)))
        logging.debug("U_pd: " + pg.bdd_sat(u_pd))

    if u_pd != pg.bdd.false:

        if debug:
            logging.debug("found vertices to update")
        r = reaches(j, u_pd, pg)

        if debug:
            logging.debug("reaches: " + pg.bdd_sat(r))

        if i % 2 == 0:
            z_r = (z & ~(r & pg.prio_odd)) & prio_lt(i, pg.p, pg)
        else:
            z_r = (z | (r & pg.prio_even)) & prio_lt(i, pg.p, pg)
        j_t = j & ~r

        if debug:
            logging.debug("z_r: " + pg.bdd_sat(z_r))
            logging.debug("xor(z, u_pd): " + pg.bdd_sat(xor(z, u_pd)))

        z_ = (z & prio_gt(i, pg.p, pg)) | xor(z & pg.p[i], u_pd) | z_r

        strat = strategy_0(z_, u_pd, pg)
        j_ = j_t | strat

        if debug:
            logging.debug("new moves: " + pg.bdd_sat_edges(strat))

    else:
        z_ = z
        strat = strategy_0(z_, u, pg)
        j_ = j | strat

        if debug:
            logging.debug("found no new vertices to update")
            logging.debug("new moves: " + pg.bdd_sat_edges(strat))
    
    return z_, j_

#@profile
def strategy_0(z: BDD, u: BDD, pg: parity_game):
    """Compute winning moves from U based on estimation Z, and all moves
    from a vertex in U if said vertex is lost by its owner.

    :param z: BDD representing estimation of vertices won by player Z
    :type z: BDD
    :param u: BDD representing vertices from which new moves are computed
    :type u: BDD
    :param pg: parity game instance
    :type pg: parity_game
    :return: BDD representing to be added to the justification graph.
    :rtype: BDD
    """

    even = u & pg.even & z
    odd = u & pg.odd & ~z
    losing = u & ~(even | odd) & pg.v # vertices won by the player that does not own it

    z_ = pg.bdd.let(pg.substitution_list, z)

    return (even & z_ & pg.e) | (odd & (~z_) & pg.e) | (losing & pg.e)

##{v ∈ V0|∃w:(v, w) ∈ E ∧ w ∈ S } ∪ { v ∈ V1| ∀w: (v, w) ∈ E ⇒ w∈S}
#@profile
def phi(z: BDD, pg: parity_game):
    """Update the estimate Z by lookahead of 1

    :param z: BDD representing vertices currently estimated to be won by Even
    :type z: BDD
    :param pg: parity game instance
    :type pg: parity_game
    :return: BDD representing new estimate Z
    :rtype: BDD
    """

    z_ = pg.bdd.let(pg.substitution_list, z)

    res = ((pg.even & pg.bdd.quantify(pg.e & z_, pg.variables_, forall=False))
        | (pg.odd & pg.bdd.quantify(~(pg.e) | z_, pg.variables_, forall=True)))
    return res

#@profile
def xor(a: BDD, b: BDD):
    return (a & ~b) | (~a & b)

#@profile
def unjustified(j: BDD, pg: parity_game):
    return  pg.v & ~pg.bdd.quantify(j, pg.variables_, forall=False)

# Set of vertices from which x can be reached over edges in j
#@profile
def reaches(j: BDD, x: BDD, pg: parity_game):
    """Compute the set of vertices from which X can be reached with moves consistent with J

    :param j: BDD representing justification graph J
    :type j: BDD
    :param x: BDD representing the originating set
    :type x: BDD
    :param pg: parity game instance
    :type pg: parity_game
    :return: BDD representing vertices from which X can be reached over J
    :rtype: BDD
    """
    # Preimage of v using edges in e
    def preimage(v: BDD, e: BDD):
        v_next = pg.bdd.let(pg.substitution_list, v)
        return pg.bdd.quantify(v_next & e, pg.variables_, forall = False)

    x_ = pg.bdd.false
    while x_ != x:
        x_ = x
        x = x | preimage(x, j)

    return x

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

    return bdd

#@profile
def prio_gt(prio: int, p: dict, pg: parity_game):
    """Returns a BDD representing all vertices with priority greater than _prio_

    :param prio: all selected vertices should have greater priority than prio
    :type prio: int
    :param p: dictionary containing BDD's for vertices of each priority
    :type p: dict
    :param pg: parity game instance
    :type pg: parity_game
    :return: bdd of all vertices with priority greater than or equal to prio
    :rtype: BDD
    """

    bdd = pg.bdd.false
    for current in p.keys():
        if current > prio:
            bdd = bdd | p[current]
    
    return bdd