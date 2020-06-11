from bdd_provider import make_bdd
from parity_game import parity_game
import subprocess
import logging

def pbes_to_pg(filename):
    # HIDEOUS AD-HOC PARSER FOR THE OUTPUT OF pbes2bdd
    # COMES WITH NO GUARANTEES

    bdd = make_bdd()

    result = subprocess.run(['pbes2bdd',filename], stdout=subprocess.PIPE).stdout.decode('ISO-8859-1')
    l = result. split('--- edges ---')
    e = l[1].strip(). replace("'''",""). replace("\n","")
    
    EDGES = str(e)
    logging.debug('Edges = %s' %(EDGES))
    l = l[0]. split('--- priorities ---')
    k = l[1]. strip()
    prio = {}
    for line in k. split('\n'):
        (v, s) = line. split('=')
        value = int(v[v.find('[')+1:v.find(']')])
        formula = str(s.strip())
        prio[value] = formula
    l = l[0]. split('--- odd nodes ---')
    ODD = l[1].strip()
    logging.debug('Odd = %s' %(ODD))
    l = l[0]. split('--- even nodes ---')
    EVEN = l[1].strip()
    logging.debug('Even = %s' %(EVEN))
    l = l[0]. split('--- all nodes ---')
    VERTICES = l[1].strip()
    logging.debug('Vertices = %s' %(VERTICES))
    l = l[0]. split('--- bdd variables ---')
    variables = [ str(variable.strip().replace("'",'')) for variable in l[1].strip().split(',')]

    (all_vars,variables_) = ([],[])
    for var in variables:
        variables_. append('%s_' %(var))
        all_vars.append('%s'%(var))
        all_vars.append('%s_'%(var))
    bdd.bdd. declare(*all_vars)

    Priorities = {}
    for i in prio:
        logging.debug('prio[%d] = %s' %(i,prio[i]))
        e = bdd.bdd.add_expr('True & %s' %(prio[i]))
        if e != bdd.bdd.false: Priorities[i] = e
    #test coherence
    e = bdd.bdd.false
    for i in Priorities:
        e = e | Priorities[i]
        for j in Priorities:
            if i != j:
                if Priorities[i] & Priorities[j] != bdd.bdd.false: print('grmbl')
    #/test
    Vertices = bdd.bdd.add_expr(VERTICES)
    if e != Vertices: print('lost some vertices?!')
    Even = bdd.bdd.add_expr(EVEN)
    Odd = bdd.bdd.add_expr(ODD)
    Edges = bdd.bdd.add_expr(EDGES)
    return parity_game(bdd, variables, variables_, Vertices, Edges, Even, Odd, Priorities)