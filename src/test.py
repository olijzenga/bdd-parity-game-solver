from dd.autoref import BDD
from parity_game import sat_to_expr
import sys

bdd = BDD()
bdd.declare('x', 'y', 'z', 'w')

# conjunction (in TLA+ syntax)
u = bdd.add_expr('x /\ y')  # operators `&, |` are supported too
print(u.support)
# substitute variables for variables (rename)
rename = dict(x='z', y='w')
v = bdd.let(rename, u)
# substitute constants for variables (cofactor)
values = dict(x=True, y=False)
v = bdd.let(values, u)
# substitute BDDs for variables (compose)
d = dict(x=bdd.add_expr('z \/ w'))
v = bdd.let(d, u)
# infix operators
v = bdd.var('z') & bdd.var('w')
v = ~ v
# quantify
u = bdd.add_expr('\E x, y:  x \/ y')
# less readable but faster alternative
u = bdd.var('x') | bdd.var('y')
u = bdd.exist(['x', 'y'], u)
assert u == bdd.true, u
# inline BDD references
u = bdd.add_expr('x /\ y | w')
# satisfying assignments (models)
d = bdd.pick(u)
sat = [d for d in bdd.pick_iter(u)]
print(sat)
n = bdd.count(u)

print("\n\n\n\n")

bdd = BDD()

bdd.declare('x0', 'x1', 'x0_', 'x1_')

e = bdd.add_expr('x0&(~x0_|x0_)&(x1<=>x1_)')

res = [ sat for sat in bdd.pick_iter(e, care_vars=['x0', 'x1', 'x0_', 'x1_']) ]
print(res)

v = bdd.add_expr('x0/\(~x1)')

image = v & e
img_ = bdd.pick_iter(image, care_vars=['x0', 'x1', 'x0_', 'x1_'])
img = bdd.quantify(image, ['x0', 'x1'], forall=False)

for sat in bdd.pick_iter(img, care_vars=['x0_', 'x1_']): print(sat)
print("\n")
for sat in bdd.pick_iter(bdd.let({'x0_':'x0', 'x1_':'x1'}, img), care_vars=['x0', 'x1']): print(sat)

print("\n\n\n")
bdd.declare('x', 'y')
expr = bdd.add_expr('x \/ y')
for sat in bdd.pick_iter(bdd.quantify(expr, ['x'], forall=True), care_vars=['x', 'y']): print(sat)

sat = { 'x': True, 'y': False }

print(sat_to_expr({ 'x': True, 'y': False }))
