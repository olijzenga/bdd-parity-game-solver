from random_parity_game_generator import random_game
from fpj import fpj
import logging
import os

s = os.environ.get('LOG_LEVEL', 'INFO')
if s == 'DEBUG': log_level = logging.DEBUG
elif s == 'INFO': log_level = logging.INFO
else: log_level = logging.INFO

logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

N = 3    # 2^N vertices
K = 2    # K priorities
J = 10   # J edges

pg = random_game(N, K, J)
logging.info(pg)
pg.show()
try :
    res = fpj(pg)
except Exception as e:
    logging.error(e)

logging.info(pg.bdd_sat(res[0]))
logging.info(pg.bdd_sat(res[1]))