from dfi import dfi
from random_parity_game_generator import random_game
import logging
from dd.autoref import BDD

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

pg = random_game(4, 2, 4)
W0, W1, S0, S1 = dfi(pg)

def edges_to_str(bdd: BDD):
    return [ pg.sat_to_hex(sat) + " <==> " + pg.sat_to_hex(sat, edge=True) for sat in pg.bdd.pick_iter(bdd, care_vars=(pg.variables + pg.variables_))]

logging.info("W0:\n" + pg.bdd_sat(W0))
logging.info("W1:\n" + pg.bdd_sat(W1))
logging.info("S0:\n" + edges_to_str(S0))
logging.info("S1:\n" + edges_to_str(S1))

pg.show()

