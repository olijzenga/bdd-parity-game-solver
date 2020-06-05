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

from bdd_provider import make_bdd
from parity_game import parity_game
import sys, os, random, math
from dd.bdd import to_pydot

# GENERATE RANDOM PARITY GAME BY GENERATING RANDOM BDDs
# DESCRIBED BY PROPOSITIONAL FORMULAE

def __LETTERS(n):
  return ['x%d' %(i) for i in range(0,n)]

def __VERTICES(n):
  letters = __LETTERS(n)
  odd = ['True']
  for l in letters:
    r = random.uniform(1,8)
    if r < 2.5: odd.append('~%s' %(l))
    if r >= 2.5 and r < 4: odd. append('%s' %(l))
  ODD = '(%s)' %('&'.join(odd))
  EVEN = '~%s' %(ODD)
  return ('True',EVEN,ODD)

def __PRIORITIES(n,k):
  letters = __LETTERS(n)
  priorities = {}
  cummulative = ['False']
  for i in range(0,k):
    priority_i = ['True']
    for l in letters:
      r = random.uniform(1,k)
      if r < 2.0: priority_i.append('~%s' %(l))
      if r >= 2.0 and r < (3.0): priority_i. append('%s' %(l))
    if i == 0: 
      priorities[i] = '(True & %s)' %('&'.join(priority_i))
      cummulative. append(priorities[i])
    elif i < k-1:
      priorities[i] = '~(%s) & (True & %s)' %('|'.join(cummulative), '&'.join(priority_i))
      cummulative. append(priorities[i])
    else:
      priorities[i] = '~(%s | False)' %('|'.join(cummulative))
  return dict(priorities)

def __EDGES(n,k,j,selfloops = True):
  # 1/j determines the likelihood that a variable may change at all; higher j, lower chance
  # k is the number of clauses
  letters = __LETTERS(n)
  letters_ = [ '%s_' %(l) for l in letters]
  edges = []
  completion = {}
  for i in range(0,k): # generate k clauses
    clause = []
    changed = []
    completion_i = []
    for i in range(len(letters)): # list the variables that *may* act as guards or *may* change; the others cannot
      if random.uniform(0,j) < 1: changed. append(i) 
    for i in range(len(letters)):
      if i in changed:
        r = random.uniform(1,6)
        if r < 2: 
          clause.append('~%s' %(letters[i]))
          completion_i.append('~%s' %(letters[i]))
        if r >= 2 and r < 4: 
          clause. append('%s' %(letters[i]))
          completion_i.append('%s' %(letters[i]))
        b = (r < 4)
        r = random.uniform(1,6)
        if r < 2:
          clause.append('~%s' %(letters_[i]))
        if r >= 2 and r < 4: 
          clause. append('%s' %(letters_[i]))
        if not(b) and r >= 4: clause. append('(%s <=> %s)' %(letters[i],letters_[i]))
      else:
        clause. append('(%s <=> %s)' %(letters[i],letters_[i]))
    completion[i] = '(%s)' %('&'. join(completion_i))
    if len(completion_i) == 0: completion[i] = '(True)'
    if len(clause) > 0:
      edges. append('(%s)' %('&'. join(clause)))
  c = [ completion[i] for i in completion.keys()]
  complement = '~(False | %s)' %('|'.join(c) ) if len(c) > 0 else 'True'
  s = []
  for i in range(len(letters)):
    s. append('(%s <=> %s)' %(letters[i],letters_[i]))
  if not(selfloops): s. append(complement)
    
  edges. append('&'.join(s))
  ret = '|'.join(edges)
  return ret


def random_game(n,k,j,debug=False,selfloops=True):
    ''' generate a random game with n variables, k priorities and j clauses
    '''
    bdd = make_bdd()  
    og_j = j

    variables = __LETTERS(n)
    (all_vars,variables_) = ([],[])
    for var in variables:
        variables_. append('%s_' %(var))
        all_vars.append('%s'%(var))
        all_vars.append('%s_'%(var))
    bdd. declare(*all_vars)
    p, Priorities = __PRIORITIES(n,k), {}
    for i in p:
        if debug: print('p[i] = %s' %(p[i]))
        e = bdd.add_expr('True & %s' %(p[i]))
        if e != bdd.false: Priorities[i] = e
    #test for coherence of the constructed graph
    e = bdd.false
    for i in Priorities:
        e = e | Priorities[i]
        for j in Priorities:
            if i != j:
                if Priorities[i] & Priorities[j] != bdd.false: print('grmbl')
    if e != bdd.true: print('lost some vertices?!')
    #/test
    (V,E,O) = __VERTICES(n)
    Ed =  __EDGES(n,k,og_j,selfloops)

    #print("Variables:" + ", ".join(variables) + "\n", "Vertices: " + V + "\n", "Even: " + E + "\n", "Odd: " + O + "\n", "Edges: " + Ed + "\n")

    Vertices = bdd.add_expr(V)
    Even = bdd.add_expr(E)
    Odd = bdd.add_expr(O)
    Edges = bdd.add_expr(Ed)
    return parity_game(bdd, variables, variables_, Vertices, Edges, Even, Odd, Priorities)


