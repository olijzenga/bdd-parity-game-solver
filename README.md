# bdd-parity-game-solver

A BDD-based parity game solver. Can generate and solve randomly generated parity games represented by BDD's. This repository is work-in-progress, so you will most likely encounter some issues while using this solver.

To use this library you should first install its dependencies using [pipenv](https://pypi.org/project/pipenv/), and enter the virtual environment:
```bash
$ pipenv install
$ pipenv shell
```

Now you can use the library. For example to run the performance testing suite do the following:
```bash
$ python src/run_games.py
```

Or you can solve and view a single parity game:
```bash
$ python src/test.py
```