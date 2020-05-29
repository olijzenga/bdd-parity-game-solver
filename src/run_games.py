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

debug = False
RANGE = range(3,35)
REPEAT_EXPERIMENTS = 1

#generate games with size (nr. Booleans) in range(3,35):
for Size_of_Games in RANGE:
  zielonka_total_time = 0.0
  dfi_total_time = 0.0
  solved_games =0
  PrioLimit = math.floor(math.sqrt(2*Size_of_Games))
  print()
  print('Solving games with %d variables and at most %d priorities' %(Size_of_Games, PrioLimit))
  for iteration in range(0, REPEAT_EXPERIMENTS):
    pg = random_game(Size_of_Games,PrioLimit, 6,False,False)

    pg_zlk = pg.copy()
    pg_dfi = pg.copy()
    pg.bdd.collect_garbage()

    # solve game using zielonka
    zielonka_solver_start = process_time()
    (W0,W1) = zlk(pg_zlk)
    solved_games += 1
    zielonka_solver_end = process_time()
    zielonka_total_time = zielonka_total_time + (zielonka_solver_end - zielonka_solver_start)
    pg.bdd.collect_garbage()

    # solve game using DFI
    dfi_solver_start = process_time()
    (W0_,W1_) = dfi(pg_dfi)
    dfi_solver_end = process_time()
    dfi_total_time = dfi_total_time + (dfi_solver_end - dfi_solver_start)
    pg.bdd.collect_garbage()

    def bdd_sat_to_text(bdd: BDD, pg: parity_game):
      return str([pg.sat_to_hex(sat) for sat in pg.bdd.pick_iter(bdd, care_vars=pg.variables)])

    # sanity checks
    if (W0 != W0_) | True:
      print("Error: difference in outcome between Zielonka and DFI")
      print("Zielonka:\nW0:" + bdd_sat_to_text(W0, pg_zlk) + "\nW1:" + bdd_sat_to_text(W1, pg_zlk) + "\n")
      print("DFI:\nW0:" + bdd_sat_to_text(W0_, pg_dfi) + "\nW1:" + bdd_sat_to_text(W1_, pg_dfi) + "\n")
      print("Game:\n" + str(pg))

      pg.make_dot("output/pg.dot")
      with open("output/pg.dot", "r") as text_file:
        s = Source(text_file.read(), filename="output/dot.png", format="png")
        s.view()
      sys. exit()
