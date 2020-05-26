from parity_game import parity_game
from dd.autoref import BDD

def zlk(pg: parity_game):
    if pg.even | pg.odd == pg.bdd.false:
      return (pg.even, pg.odd)
    else:
      p = max_prio(pg.p)
      parity = 'even' if p%2 == 0 else 'odd'
      U = pg.p[p]
      A = pg.attractor (parity, U)
      G = pg.copy()
      G.remove(A)
      (W0, W1) = zlk(G)
      if parity == 'even' and W1 == pg.bdd.false:
        return (W0 | A, W1)
      elif parity == 'odd' and W0 == pg.bdd.false:
        return (W0, A| W1)
      else:
        (W, opponent) = (W1, 'odd') if parity == 'even' else (W0, 'even')
        B = pg.attractor(opponent, W)
        H = pg.copy()
        H.remove(B)
        (X0, X1) = zlk(H)
        if parity == 'even': return (X0, X1 | B) 
        else: return (X0 | B, X1)

def max_prio(p: dict):
    return max(p)