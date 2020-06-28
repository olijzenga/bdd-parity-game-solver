import os
import sys
import subprocess
import json
import time

if len(sys.argv) < 2:
    print("empirical_evaluation.py [output_file]")
    exit(1)

output_file = sys.argv[1]
ALGORITHMS = ["dfi", "dfi-ns", "fpj", "zlk"]
NR_ROUNDS = 5

# Mapping of experiment file name prefixes to their benchmark set name
benchmarks = {
    "amba_decomposed" : "Parameterized AMBA bus controller",
    "detector" : "Parameterized detector",
    "full_arbiter" : "Parameterized arbiters",
    "lilydemo" : "Lily benchmark set",
    "load" : "Parameterized load balancer",
    "ltl2dba" : "Parameterized LTL to Buchi translations",
    "ltl2dpa" : "Parameterized LTL to Buchi translations",
    "prioritized_arbiter" : "Parameterized arbiters",
    "round_robin_arbiter" : "Parameterized arbiters",
    "simple_arbiter" : "Parameterized arbiters",
    "starve" : "Parameterized generalized buffer",
}

# Runs all cases in experiments/syntcomp NR_ROUNDS times for each algortihm in ALGORITHMS.
# Results are written to a CSV file which allows for easy analysis of the results using .e.g
# Google Sheets. Each parity game solve is run in a separate process, and the explicit game
# from the source file will be converted to an explicit game every time, which makes this process
# rather slow. NOTE: conversion time form explicit to symbolic is not included in the recorded solving time
with open(output_file, 'w') as file:
    # Write table headers
    file.write("Set, File, Algorithm, Time, PG Vertices, Priorities, Start Memory (MB), Start BDD Nodes, Start Peak Live BDD Nodes, Start Peak BDD Nodes, End Memory (MB), End BDD Nodes, End Peak Live BDD Nodes, End Peak BDD Nodes, SAT count, Avg. out degree\r\n")
    # Do 5 rounds, each round each algorithm is run on each parity game
    for i in range(NR_ROUNDS):
        # 10 second pause in between every round
        time.sleep(10)
        print("Evaluation round {0}".format(i + 1))
        # Solve each parity game once using each algorithm
        files = os.listdir("experiments/syntcomp/")
        for j in range(len(files)):
            file_name = files[j]
            # Filter only for .oink files, only files in pgsolver format will work.
            if file_name.endswith(".oink"):
                print("Solving parity game {0} (game {1}/{2} of round {3}/{4})".format(file_name, j+1, len(files)+1, i+1, NR_ROUNDS))

                # Solve each parity game using all algorithms, but in separate processes
                for algorithm in ALGORITHMS:
                    print(algorithm)
                    # Run each solve using a separate python process as a shell command. This means that each Python
                    # process is independent so parity game runs will not influence each other through shared
                    # resources. Running in quiet mode with an oink file only makes src/main.py output a JSON with results
                    # and extra data. We immediately decode this JSON into res.
                    res = json.loads(subprocess.run([
                        "python", 
                        "src/main.py", 
                        "--oink", 
                        "--source=./experiments/syntcomp/{0}".format(file_name), 
                        "--{0}".format(algorithm), 
                        "--quiet"]
                        , stdout=subprocess.PIPE
                    ).stdout.decode('utf-8'))

                    # Try map the pg case to its benchmark set.
                    benchmarkset = "Notfound"
                    for prefix in benchmarks.keys():
                        if file_name.startswith(prefix):
                            benchmarkset = benchmarks[prefix]
                            break
                
                    # Build a CSV row out of the algorithm run
                    line = ", ".join([ str(x) for x in [
                        benchmarkset,                                   # Benchmark set
                        file_name,                                      # File name
                        algorithm,                                      # Algorithm
                        res["times"][algorithm.replace('-', '_')],      # Time
                        res["nr_of_vertices_pg"],                       # Number of vertices in parity game
                        res["d"],                                       # d
                        res["stats_start"]["mem"],                      # Current memory usage in MB
                        res["stats_start"]["n_nodes"],                  # Current number of live nodes
                        res["stats_start"]["peak_live_nodes"],          # Peak number of live nodes
                        res["stats_start"]["peak_nodes"],               # Peak number of nodes
                        res["stats_end"]["mem"],                        # Current memory usage in MB
                        res["stats_end"]["n_nodes"],                    # Current number of live nodes
                        res["stats_end"]["peak_live_nodes"],            # Peak number of live nodes
                        res["stats_end"]["peak_nodes"],                 # Peak number of nodes
                        res["sat_count"],                               # SAT count of entire game
                        res["avg_out_deg"]                              # Average outgoing degree of game
                    ]]) + "\r\n" 
                    file.write(line)