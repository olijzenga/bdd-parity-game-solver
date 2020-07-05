# BDD Parity Game Solver

A BDD-based parity game solver. Implements symbolic fpj, dfi, dfi-ns and zlk. Can run games in pgsolver format, or random games using a crappy internal random game generator which should NOT be used for empirical evaluations. Includes a script for automatically reproducing the emprical evaluation of the published paper on this solver, and exporting results to a CSV file (`scripts/empirical.py`). Also includes the output data from our empirical evaluation in the paper (`output/empirical.csv.dist`).

Also includes parity games in pgsolver format from the SYNTCOMP2020 _pgame_ track which consists of parity automatons converted to parity games using [knor](https://github.com/trolando/knor).

## Setup

Dependencies of this repository can be found in `requirements.txt`. The [dd](https://github.com/tulip-control/dd) BDD package has to be manually installed because installation options are required to include CUDD. Install options cause errors in installing from requirements.txt. A full installation is as follows:

```bash
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
# Manually install dd
$ pip install dd --install-option="--fetch" --install-option="--cudd"
```

## Usage

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