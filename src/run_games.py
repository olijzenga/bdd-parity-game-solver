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
from time import process_time
import sys, os, random, math
from graphviz import Source
from dd.autoref import BDD
from math import floor
import logging

s = os.environ.get('LOG_LEVEL', 'INFO')
if s == 'DEBUG': log_level = logging.DEBUG
elif s == 'INFO': log_level = logging.INFO
else: log_level = logging.INFO

logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

game_sizes_range = range(3,35)
games_per_size = 20

#generate games with size (nr. Booleans) in range(3,35):
for game_size in game_sizes_range:
  zlk_total_time = 0.0
  dfi_total_time = 0.0
  d = math.floor(math.sqrt(2*game_size))
  for iteration in range(0, games_per_size):
    pg = random_game(game_size, d, 4, False, False)

    pg_zlk = pg.copy()
    pg_dfi = pg.copy()
    pg.bdd.collect_garbage()
    pg_zlk.bdd.collect_garbage()
    pg_dfi.bdd.collect_garbage()

    # solve game using zielonka
    zlk_solver_start = process_time()
    (W0,W1) = zlk(pg_zlk)
    zlk_solver_end = process_time()
    zlk_total_time += zlk_solver_end - zlk_solver_start
    pg.bdd.collect_garbage()

    # solve game using DFI
    dfi_solver_start = process_time()
    (W0_,W1_) = dfi(pg_dfi)
    dfi_solver_end = process_time()
    dfi_total_time = dfi_total_time + (dfi_solver_end - dfi_solver_start)
    pg.bdd.collect_garbage()

    nr_vertices_ = str(pow(2, game_size)).rjust(5)
    d_ = str(d).rjust(5)
    iteration_ = str(iteration).rjust(5)
    zlk_total_time_ = str(floor(zlk_total_time)).rjust(10)
    dfi_total_time_ = str(floor(dfi_total_time)).rjust(10)
    logging.info("|V| = {0} d = {1} | game {2} | zlk time: {3} | dfi time: {4}".format(nr_vertices_, d_, iteration_, zlk_total_time_, dfi_total_time_))

    def bdd_sat_to_text(bdd: BDD, pg: parity_game):
      return str([pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(bdd, care_vars=pg.variables)])

    # sanity checks
    if (W0 != W0_):
      logging.error("Error: difference in outcome between Zielonka and DFI")
      logging.error("Zielonka:\nW0:" + bdd_sat_to_text(W0, pg_zlk) + "\nW1:" + bdd_sat_to_text(W1, pg_zlk) + "\n")
      logging.error("DFI:\nW0:" + bdd_sat_to_text(W0_, pg_dfi) + "\nW1:" + bdd_sat_to_text(W1_, pg_dfi) + "\n")
      logging.error("Game:\n" + str(pg))

      pg.make_dot("output/pg.dot")
      with open("output/pg.dot", "r") as text_file:
        s = Source(text_file.read(), filename="output/dot.png", format="png")
        s.view()
      sys. exit()
