from dd.cudd import BDD

# Allows for easy repository-wide change of dd backend.
# Note that some stuff will break when using a different backend.
# Using the pure python autoref backend is relatively free of problems.
# Only the 'statistics' function is not present which causes errors in
# main.py so these should be removed in that case.
def make_bdd():
    return BDD()