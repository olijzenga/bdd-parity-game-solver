from dfi import dfi
from random_parity_game_generator import random_game
import logging

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

pg = random_game(4, 2, 4)
W0, W1 = dfi(pg)

logging.info("W0:\n" + pg.bdd_sat(W0))
logging.info("W1:\n" + pg.bdd_sat(W1))

pg.show()

