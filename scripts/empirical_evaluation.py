import os
import sys
import subprocess
import json

if len(sys.argv) < 2:
    print("empirical_evaluation.py [output_file]")
    exit(1)

output_file = sys.argv[1]
ALGORITHMS = ["dfi", "dfi-ns", "fpj", "zlk"]

with open(output_file, 'w') as file:
    # Write table headers
    file.write("File, Algorithm, Time, PG Vertices, Priorities, Memory (MB), BDD Nodes, Peak Live BDD Nodes, Peak BDD Nodes\r\n")
    for file_name in sorted(os.listdir("experiments/syntcomp/")):
        if file_name.endswith(".oink"):
            print("Solving parity game {0}".format(file_name))

            for algorithm in ALGORITHMS:
                print(algorithm)
                res = subprocess.run([
                    "python", 
                    "src/main.py", 
                    "--oink", 
                    "--source=./experiments/syntcomp/{0}".format(file_name), 
                    "--{0}".format(algorithm), 
                    "--quiet"]
                    , stdout=subprocess.PIPE
                ).stdout.decode('utf-8')
                
                stats = json.loads(("{" + (res.split("{")[1])).replace("'", "\""))
                line = "\"{0}\"".format(file_name)                          # File name
                line += ", " + algorithm                                    # Algorithm
                line += ", " + str(float(res.split(",")[0].split(":")[1]))  # Time
                line += ", " + str(float(res.split(",")[1].split(":")[1]))  # Number of vertices in parity game
                line += ", " + str(int(res.split(",")[2].split(":")[1]))    # d
                line += ", " + str(stats["mem"])                            # Current memory usage in MB
                line += ", " + str(stats["n_nodes"])                        # Current number of live nodes
                line += ", " + str(stats["peak_live_nodes"])                # Peak number of live nodes
                line += ", " + str(stats["peak_nodes"])                     # Peak number of nodes
                line += "\r\n" 
                file.write(line)