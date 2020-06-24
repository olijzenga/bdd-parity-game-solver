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

benchmarks = {
    "amba_decomposed" : "Parameterized AMBA bus controller",
    "detector" : "Parameterized detector",
    "full_arbiter" : "Parameterized arbiters",
    "lilydemo" : "Lily benchmark set",
    "load" : "Parameterized load balancer",
    #"loadcomp" : "Parameterized load balancer",
    #"loadfull" : "Parameterized load balancer",
    "ltl2dba" : "Parameterized LTL to Buchi translations",
    "ltl2dpa" : "Parameterized LTL to Buchi translations",
    "prioritized_arbiter" : "Parameterized arbiters",
    "round_robin_arbiter" : "Parameterized arbiters",
    "simple_arbiter" : "Parameterized arbiters",
    "starve" : "Parameterized generalized buffer",
}

with open(output_file, 'w') as file:
    # Write table headers
    file.write("Set, File, Algorithm, Time, PG Vertices, Priorities, Start Memory (MB), Start BDD Nodes, Start Peak Live BDD Nodes, Start Peak BDD Nodes, End Memory (MB), End BDD Nodes, End Peak Live BDD Nodes, End Peak BDD Nodes\r\n")
    for i in range(5):
        time.sleep(5)
        print("Evaluation round {0}".format(i + 1))
        for file_name in os.listdir("experiments/syntcomp/"):
            if file_name.endswith(".oink"):
                print("Solving parity game {0} (round {1})".format(file_name, i+1))

                for algorithm in ALGORITHMS:
                    print(algorithm)
                    res = json.loads(subprocess.run([
                        "python", 
                        "src/main.py", 
                        "--oink", 
                        "--source=./experiments/syntcomp/{0}".format(file_name), 
                        "--{0}".format(algorithm), 
                        "--quiet"]
                        , stdout=subprocess.PIPE
                    ).stdout.decode('utf-8'))

                    benchmarkset = "Notfound"
                    for prefix in benchmarks.keys():
                        if file_name.startswith(prefix):
                            benchmarkset = benchmarks[prefix]
                            break
                
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
                    ]]) + "\r\n" 
                    file.write(line)