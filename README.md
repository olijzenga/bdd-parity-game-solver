# bdd-parity-game-solver

A BDD-based parity game solver. Can generate and solve randomly generated parity games represented by BDD's. This repository is work-in-progress, so you will most likely encounter some issues while using this solver.

Dependencies of this repository can be found in `requirements.txt`. If there are problems installing the [dd](https://github.com/tulip-control/dd) BDD package, please refer to their repository for installation instructions. If you cannot get CUDD with Cython to work, try the pure Python autoref BDD backend included in the dd package.

To run a random parity game with e.g. fpj and dfi (available algorithms are dfi, dfi-ns, fpj and zlk):
```bash
$ python src/main.py --random --dfi --fpj
```

To only output the result of a solve of `src/main.py`, and not intermediate progress logs, use the `--quiet` option.
```bash
$ python src/main.py --random --dfi --fpj --quiet
```

Solve a parity game from a file in pgsolver format as shown below. Note that the output solving time does not include the naive conversion from explicit to symbolic.
```bash
$ python src/main.py --oink --source=somefile.oink --dfi --fpj
```

The exact experiments from the paper can easily be repeated as shown below. This outputs all data used in the evaluation to the specified output file in csv format which can easily be imported into e.g. Google Sheets.
```bash
$ python scripts/empirical_evaluation.py [output_file]
```