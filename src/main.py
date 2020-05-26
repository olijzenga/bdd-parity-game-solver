from random_parity_game_generator import random_game
from dfi import dfi_no_freeze

N = 3    # 2^N vertices
K = 2    # K priorities
J = 10   # J edges

pg = random_game(N, K, J)
res = dfi_no_freeze(pg)

print(res)