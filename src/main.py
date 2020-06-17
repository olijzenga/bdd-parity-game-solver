from random_parity_game_generator import random_game
from fpj import fpj
from dfi import dfi
from zlk import zlk
from pbes_to_pg import pbes_to_pg
import logging
import os
from time import process_time, time
import getopt, sys
import random
from run_games import validate_strategy, compare_results

s = os.environ.get('LOG_LEVEL', 'INFO')
if s == 'DEBUG': log_level = logging.DEBUG
elif s == 'INFO': log_level = logging.INFO
else: log_level = logging.INFO

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

N = 50    # 2^N vertices
D = 4    # K priorities
J = 8   # J 'clauses' (edges)
SEED = None

GAME_SRC = None
PBES_SRC = None

ALGORITHMS = []

try:
    opts, args = getopt.getopt(sys.argv[1:], [],["random", "pbes", "dfi", "fpj", "zlk", "source=", "seed=", "n=", "d=", "j="])
except getopt.GetoptError as e:
    logger.error(e)
    logger.error("Could not get run arguments")
    sys.exit(2)
for opt, arg in opts:
    if opt == "--random":
        if GAME_SRC:
            raise Exception("Only one game source allowed at a time")
        GAME_SRC = "random"
    elif opt == "--pbes":
        if GAME_SRC:
            raise Exception("Only one game source allowed at a time")
        GAME_SRC = "pbes"
    elif opt == "--zlk":
        ALGORITHMS.append(zlk)
    elif opt == "--dfi":
        ALGORITHMS.append(dfi)
    elif opt == "--fpj":
        ALGORITHMS.append(fpj)
    elif opt == "--source":
        if not GAME_SRC == "pbes":
            raise Exception("--pbes flag not set")
        PBES_SRC = arg
    elif opt == "--seed":
        if not GAME_SRC == "random":
            raise Exception("--random flag not set")
        SEED = int(arg)
    elif opt == "--n":
        if not GAME_SRC == "random":
            raise Exception("--random flag not set")
        N = int(arg)
    elif opt == "--d":
        if not GAME_SRC == "random":
            raise Exception("--random flag not set")
        D = int(arg)
    elif opt == "--j":
        if not GAME_SRC == "random":
            raise Exception("--random flag not set")
        J = int(arg)

    if GAME_SRC == "pbes" and not PBES_SRC:
        raise Exception("Game source set to pbes but no file provided")

    if GAME_SRC == "pbes":
        raise Exception("PBES support not implemented")

if GAME_SRC == "random":
    if not SEED:
        SEED = time() * 256
    logger.info("Random game with seed {0}, N {1}, D {2} J {3}".format(SEED, N, D, J))
    pg = random_game(SEED, N, D, J, False, False)

logger.info("Parity game properties:")
logger.info("BDD sizes: vertices={0} edges={1} priorities={2}".format(pg.v.dag_size, pg.e.dag_size, sum([ pg.p[prio].dag_size for prio in pg.p])))

res = {}
for algorithm in ALGORITHMS:
    name = algorithm.__name__
    game = pg.copy(deep=True)
    start = process_time()
    result = algorithm(game)
    end = process_time()

    res[name] = { "time": end - start, "res": result, "game": game }

logging.info(", ".join([ "{0}: {1}".format(name, "%10.3f"%(res[name]["time"])) for name in res ]))

logging.info("Comparing results...")
if not compare_results({ r : res[r] for r in res }):
    sys.exit()
logging.info("Winning area consistent accross all algorithms")

logging.info("Validating strategies...")
bad_strat = False
for name in res.keys():
    r = res[name]["res"]
    game = res[name]["game"]
    if len(r) == 4:
        if not validate_strategy(r[0], r[1], r[2], r[3], game, name):
            bad_strat = True

if bad_strat:
    logging.error("Invalid strategy detected")
    sys.exit()
logging.info("Success")

#logger.info(pg.bdd_sat(res[0]))
#logger.info(pg.bdd_sat(res[1]))