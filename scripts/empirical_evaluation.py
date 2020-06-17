import os
import sys
import subprocess

if len(sys.argv) < 2:
    print("empirical_evaluation.py [output_file]")
    exit(1)

output_file = sys.argv[1]
ALGORITHMS = ["dfi", "dfi-ns", "fpj", "zlk"]

with open(output_file, 'w') as file:
    # Write table headers
    file.write("File, Algorithm, Time, PG Vertices\r\n")
    for file_name in sorted(os.listdir("experiments/syntcomp/")):
        if file_name.endswith(".oink"):
            print("Solving parity game {0}".format(file_name))

            cmd = "python src/main.py --oink --source=\"./experiments/syntcomp/{0}\" --{1} --quiet"
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
                
                line = "\"{0}\"".format(file_name)
                line += ", " + algorithm
                line += ", " + str(float(res.split(",")[0].split(":")[1]))
                line += ", " + str(float(res.split(",")[1].split(":")[1]))
                line += "\r\n"
                # print(res)
                # print(res.split(","))
                file.write(line)