from random_parity_game_generator import random_game
from fpj import fpj
from dfi import dfi
from zlk import zlk
from pbes_to_pg import pbes_to_pg
from pg import read_parity_game as read_oink, oink_to_sym
import logging
import os
from time import process_time, time, sleep
import getopt, sys
import random
from run_games import validate_strategy, compare_results
import json

s = os.environ.get('LOG_LEVEL', 'INFO')
if s == 'DEBUG': log_level = logging.DEBUG
elif s == 'INFO': log_level = logging.INFO
else: log_level = logging.INFO

N = 50    # 2^N vertices
D = 4    # K priorities
J = 8   # J 'clauses' (edges)
SEED = None

GAME_SRC = None
PG_RESOURCE = None
QUIET_MODE = False

ALGORITHMS = []

try:
    opts, args = getopt.getopt(sys.argv[1:], [],["random", "pbes", "oink", "dfi", "dfi-ns", "fpj", "zlk", "source=", "seed=", "n=", "d=", "j=", "quiet"])
except getopt.GetoptError as e:
    print(e)
    print("Could not get run arguments")
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
    elif opt == "--oink":
        if GAME_SRC:
            raise Exception("Only one game source allowed at a time")
        GAME_SRC = "oink"
    elif opt == "--zlk":
        ALGORITHMS.append(zlk)
    elif opt == "--dfi":
        ALGORITHMS.append(dfi)
    elif opt == "--dfi-ns":
        def dfi_ns(pg): return dfi(pg, strategy=False)
        ALGORITHMS.append(dfi_ns)
    elif opt == "--fpj":
        ALGORITHMS.append(fpj)
    elif opt == "--source":
        if not GAME_SRC in ["pbes", "oink"]:
            raise Exception("pbes or oink flag not set")
        PG_RESOURCE = arg
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
    elif opt == "--quiet":
        QUIET_MODE=True

if GAME_SRC in ["pbes", "oink"] and not PG_RESOURCE:
    raise Exception("Game source set to file, but resource not provided")

if GAME_SRC == "pbes":
    raise Exception("PBES support not implemented")

if QUIET_MODE:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.FATAL)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.FATAL)
else:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

if GAME_SRC == "random":
    if not SEED:
        SEED = time() * 256
    logger.info("Random game with seed {0}, N {1}, D {2} J {3}".format(SEED, N, D, J))
    pg = random_game(SEED, N, D, J, False, False)

if GAME_SRC == "oink":
    oink_pg = read_oink(PG_RESOURCE)
    pg = oink_to_sym(oink_pg)
    sleep(0.5)
    stats_start = pg.bdd.statistics(exact_node_count=True)

logger.info("Parity game properties:")
logger.info("BDD sizes: vertices={0} edges={1} priorities={2}".format(pg.v.dag_size, pg.e.dag_size, sum([ pg.p[prio].dag_size for prio in pg.p])))

res = {}
for algorithm in ALGORITHMS:
    name = algorithm.__name__
    game = pg.copy(deep=True)
    start = time()
    result = algorithm(game)
    end = time()

    res[name] = { "time": end - start, "res": result, "game": game }

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

if not GAME_SRC == "oink":
    print(", ".join([ "{0}: {1}".format(name, "%14.6f"%(res[name]["time"])) for name in res ]))
else:
    sleep(1)
    out = { name : res[name]["time"] for name in res.keys() }
    print(json.dumps( { "times": out, "sat_count": game.get_sat_count(), "avg_out_dev": game.get_avg_out_deg(), "nr_of_vertices_pg": str(len(oink_pg.nodes())).rjust(10), "d": game.d, "stats_start": stats_start, "stats_end": game.bdd.statistics(exact_node_count=True) }))

#logger.info(pg.bdd_sat(res[0]))
#logger.info(pg.bdd_sat(res[1]))