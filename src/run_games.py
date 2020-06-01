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
from dfi import dfi
from zlk import zlk
from fpj import fpj
from time import process_time
import sys, os, random, math
from dd.autoref import BDD
from math import floor
import logging
import cProfile, pstats

s = os.environ.get('LOG_LEVEL', 'INFO')
if s == 'DEBUG': log_level = logging.DEBUG
elif s == 'INFO': log_level = logging.INFO
else: log_level = logging.INFO

logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
profiler = cProfile.Profile()
do_profiling = False

game_sizes_range = range(5,35)
games_per_size = 5000

#generate games with size (nr. Booleans) in range(3,35):
for game_size in game_sizes_range:
  algorithms = [zlk, dfi, fpj]
  profiling = []
  total_solving_times = [ 0 for _ in algorithms ]
  d = math.floor(math.sqrt(2*game_size))
  for iteration in range(0, games_per_size):
    pg = random_game(game_size, d, 4, False, False)

    logging.debug(str(pg))

    games = [ pg.copy() for _ in algorithms ]
    for game in games: game.bdd.collect_garbage()
    pg.bdd.collect_garbage()

    results = [ None for _ in algorithms ]
    for i in range(len(algorithms)):
        algorithm = algorithms[i]
        game = games[i]

        if algorithm.__name__ in profiling:
            profiler.enable()

        start_time = process_time()
        res = algorithm(game)
        end_time = process_time()

        if algorithm.__name__ in profiling:
            profiler.disable()

        total_solving_times[i] += end_time - start_time
        results[i] = res
        game.bdd.collect_garbage()

    nr_vertices_ = str(pow(2, game_size)).rjust(5)
    d_ = str(d).rjust(5)
    iteration_ = str(iteration).rjust(5)
    text = "|V| = {0} d = {1} | game {2}".format(nr_vertices_, d_, iteration_)

    for i in range(len(algorithms)):
        text += "| {0} time: {1}".format(algorithms[i].__name__, ("%10.3f"%total_solving_times[i]).rjust(10))
    logging.info(text)

    def bdd_sat_to_hex(bdd: BDD, pg: parity_game):
      return [pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(bdd, care_vars=pg.variables)]

    def show_results_diff(i, j):
        logging.error("Error: difference in outcome between algorithms")

        logging.error("{0}:\nW0: {1}\nW1: {2}".format(algorithms[i].__name__, str(bdd_sat_to_hex(results[i][0], games[i])), str(bdd_sat_to_hex(results[i][1], games[i]))))
        logging.error("{0}:\nW0: {1}\nW1: {2}".format(algorithms[j].__name__, str(bdd_sat_to_hex(results[j][0], games[i])), str(bdd_sat_to_hex(results[j][1], games[j]))))
        logging.error("Difference: {0}".format(str(set(bdd_sat_to_hex(results[i][0], games[i])).symmetric_difference(set(bdd_sat_to_hex(results[j][0], games[j]))))))

        logging.error("Game:\n" + str(pg))
        pg.show()

    # sanity checks
    j = None
    for i in range(len(algorithms)):
        result = results[i]

        if(j != None and (results[j][0] != result[0] or results[j][1] != result[1])):
            show_results_diff(i, j)
            sys.exit()
        
        j = i
        
        if(len(result) == 4):
            # TODO: validate strategy
            pass

  if profiling:
    stats = pstats.Stats(profiler, stream=sys.stdout)
    stats.sort_stats('time')
    stats.print_stats()
