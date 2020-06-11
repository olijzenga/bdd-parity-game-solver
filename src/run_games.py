# (C) 2018 - TECHNISCHE UNIVERSITEIT EINDHOVEN
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED,INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES
# OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# THIS SOFTWARE IS PART OF THE TU/e COMPUTER SCIENCE REPORT 2018-01
# Citation for published version:
#
# Sanchez, L., Wesselink, J.W., & Willemse, T.A.C. (2018). BDD-based parity game solving: a comparison of
# Zielonka's recursive algorithm, priority promotion and fixpoint iteration. (Computer science reports; Vol. 1801).
# Eindhoven: Technische Universiteit Eindhoven.
# https://pure.tue.nl/ws/files/92755535/CSR_18_01.pdf



from random_parity_game_generator import random_game
from parity_game import parity_game
from dfi import dfi, dfi_no_freezing
from zlk import zlk
from fpj import fpj
from time import process_time, sleep
import sys, os, random, math, getopt
from dd.autoref import BDD
from math import floor
import logging
from pyinstrument import Profiler
import matplotlib.pyplot as plt

#
#   Initialization code
#
s = os.environ.get('LOG_LEVEL', 'INFO')
if s == 'DEBUG': log_level = logging.DEBUG
elif s == 'INFO': log_level = logging.INFO
else: log_level = logging.INFO

logger = logging.getLogger(__name__)
profiler = Profiler()

profile_algo = os.environ.get('PROFILE', '') # Name of the algorithm to profile

DO_PLOT = False
PLOT_COLORS = ["green", "red", "blue", "yellow", "black", "purple"]
NR_OF_EXPERIMENTS = 50
STARTING_GAME_SIZE = 50

games_per_size = 500

algorithms = [zlk, dfi, dfi_no_freezing, fpj]
total_solving_times = [ 0 for _ in algorithms ]
results = { a.__name__ : None for a in algorithms }
games = [ None for _ in algorithms ]
pg = None

# Stores average run time of each algorithm for all tested combinaitons of d and |V|
plot_db = []

#
# End of initialization
#

def run_games():
    global total_solving_times
    global results
    global games
    global pg
    global plot_db

    if profile_algo:
        logging.info("Profiling for algorithm " + profile_algo)

    print(game_sizes_range)
    for game_size in game_sizes_range:
        D = 4
        J = 16
        for iteration in range(0, games_per_size):
            seed = random.randint(0, 1000000000000)
            pg = random_game(seed, game_size, D, J, False, False)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(str(pg))

            games = [ pg.copy() for _ in algorithms ]
            #for game in games: game.bdd.collect_garbage()
            #pg.bdd.collect_garbage()

            for i in range(len(algorithms)):
                algorithm = algorithms[i]
                game = games[i]

                if algorithm.__name__ == profile_algo:
                    profiler.start()

                start_time = process_time()
                res = algorithm(game)
                end_time = process_time()

                if algorithm.__name__ == profile_algo:
                    profiler.stop()

                total_solving_times[i] += end_time - start_time
                results[algorithm.__name__] = res
                #game.bdd.collect_garbage()

            nr_vertices_ = str(game_size).rjust(5)
            d_ = str(D).rjust(5)
            j_ = str(J).rjust(5)
            iteration_ = str(iteration).rjust(5)
            seed_ = str(seed).rjust(15)
            text = "seed = {0} n = {1} d = {2} j = {3} | game {4}".format(seed_, nr_vertices_, d_, j_, iteration_)

            for i in range(len(algorithms)):
                text += " | {0} time: {1}".format(algorithms[i].__name__, ("%10.3f"%total_solving_times[i]).rjust(10))
            logger.info(text)

            if not compare_results(results, pg):                
                sys.exit()

            # sanity checks
            for name in results.keys():
                result = results[name]               
                if len(result) == 4:
                    if not validate_strategy(result[0], result[1], result[2], result[3], pg, name):
                        logger.error("BDD sizes: vertices={0} edges={1} priorities={2}".format(pg.v.dag_size, pg.e.dag_size, sum([ pg.p[prio].dag_size for prio in pg.p])))
                        show_single_result(result, pg, name)
                        sys.exit()

        # Capture results for plotting
        plot_db.append({ 'd': D, '|V|': game_size, 'avgs': { algorithms[i].__name__ : (total_solving_times[i] / games_per_size) for i in range(len(algorithms)) } })

        total_solving_times = [ 0 for _ in algorithms ]

    if profile_algo:
        logging.info("Showing profiler results:")
        profiler.output_text(unicode=True, color=True)

def compare_results(results, game):
    prev = None
    for name in results.keys():
        result = results[name]

        if prev != None and (results[prev][0] != result[0] or results[prev][1] != result[1]):
            show_results_diff(result, name, results[prev], prev, game)
            return False
        
        prev = name
    return True

def bdd_sat_to_hex(bdd: BDD, pg: parity_game):
      return [pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(bdd, care_vars=pg.variables)]

def show_results_diff(res0, name0, res1, name1, game):
    logger.error("Error: difference in outcome between algorithms")
    logger.error("BDD sizes: vertices={0} edges={1} priorities={2}".format(game.v.dag_size, game.e.dag_size, sum([ game.p[prio].dag_size for prio in game.p])))

    logger.error("{0}:\nW0: {1}\nW1: {2}".format(name0, str(bdd_sat_to_hex(res0[0], game)), str(bdd_sat_to_hex(res0[1], game))))
    logger.error("{0}:\nW0: {1}\nW1: {2}".format(name1, str(bdd_sat_to_hex(res1[0], game)), str(bdd_sat_to_hex(res1[1], game))))
    logger.error("Difference: {0}".format(str(set(bdd_sat_to_hex(res0[0], game)).symmetric_difference(set(bdd_sat_to_hex(res1[0], game))))))

    logger.error("Game:\n" + str(game))
    pg.show()

# Requires result to have a strategy
def show_single_result(result, pg, name):
    (w0, w1, s0, s1) = result

    logger.error("Result for algorithm {0}:".format(name))
    logger.error("{0}:\nW0: {1}\nW1: {2}".format(name, str(bdd_sat_to_hex(w0, pg)), str(bdd_sat_to_hex(w1, pg))))
    logger.error("{0}:\nS0: {1}\nS1: {2}".format(
        name, 
        str(pg.bdd_sat_edges(s0)),
        str(pg.bdd_sat_edges(s1))
    ))

    logger.error("Game:\n" + str(pg))
    pg.show()

def validate_strategy(w0: BDD, w1: BDD, s0: BDD, s1: BDD, pg: parity_game, name: str):
    if (w0 & pg.even & s0) != s0:
        logger.error("{0}: Strategy for Even does not cover all vertices won and controlled by Even".format(name))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Missing vertices: " + pg.bdd_sat(pg.bdd.quantify((pg.even & w0) & ~s0, pg.variables_)))
        return False

    if (w1 & pg.odd & s1) != s1:
        logger.error("{0}: Strategy for Odd does not cover all vertices won and controlled by Odd".format(name))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Missing vertices: " + pg.bdd_sat(pg.bdd.quantify((pg.odd & w1) & ~s1, pg.variables_)))
        return False

    if (~pg.even & s0) != pg.bdd.false:
        logger.error("{0}: Strategy for Even contains moves from vertices controlled by Odd".format(name))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Bad moves: " + pg.bdd_sat_edges(~pg.even & s0))
        return False

    if (~pg.odd & s1) != pg.bdd.false:
        logger.error("{0}: Strategy for Odd contains moves from vertices controlled by Even".format(name))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Bad moves: " + pg.bdd_sat_edges(~pg.odd & s1))
        return False

    if (s0 & pg.bdd.let(pg.substitution_list, w1)) != pg.bdd.false:
        logger.error("{0}: Strategy of Even contains a move to the winning area of Odd".format(name))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Wrong moves: " + pg.bdd_sat_edges(s0 & pg.bdd.let(pg.substitution_list, w1)))
        return False

    if (s1 & pg.bdd.let(pg.substitution_list, w0)) != pg.bdd.false:
        logger.error("{0}: Strategy of Odd contains a move to the winning area of Even".format(name))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Wrong moves: " + pg.bdd_sat_edges(s1 & pg.bdd.let(pg.substitution_list, w0)))
        return False

    return True

def show_results_plot(data):
    
    x = [ str(d['|V|']) for d in data ]
    x_ = list(range(len(x)))
    plt.xticks(x_, x)

    for i in range(len(algorithms)):
        name = algorithms[i].__name__
        color = PLOT_COLORS[i]

        y = [ d['avgs'][name] for d in data ]
        plt.plot(x_, y, color=color)

    plt.xlabel("Nr of vertices (=2^x)")
    plt.ylabel("Average runtime (s)")
    plt.legend([ a.__name__ for a in algorithms ])
    plt.title("Average runtime for each algorithm at each game size (d=4)")

    # Reduce font size of x and y axis to fit more game sizes
    plt.rc('axes', labelsize=8)

    plt.savefig("output/plot.png")


if __name__ == "__main__":
    print("here")

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "p",["n=", "plot", "profile="])
    except getopt.GetoptError:
        logger.error("Could not get run arguments")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--plot"):
            DO_PLOT = True
        elif opt == "--profile":
            profile_algo = arg
        elif opt == "--n":
            NR_OF_EXPERIMENTS = int(arg)

    game_sizes_range = range(STARTING_GAME_SIZE, STARTING_GAME_SIZE + NR_OF_EXPERIMENTS)

    logger.info("Running {0} experiments".format(NR_OF_EXPERIMENTS))
    logger.info("Graph plotting {0}".format("enabled" if DO_PLOT else "disabled"))

    sleep(0.5)

    run_games()

    if DO_PLOT:
        show_results_plot(plot_db)
 