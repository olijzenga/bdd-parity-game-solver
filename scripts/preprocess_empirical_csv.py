import os, sys

if len(sys.argv) < 3:
    print("preprocess_emprical_csv.py [input_file] [output_file]")
    exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Mapping from experiment file prefixes to their collection name
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

try:
    with open(input_file, 'r') as input:
        input_lines = input.readlines()
except Exception as e:
    print(e)
    exit(1)

with open(output_file, 'w') as output:
    # Write csv file header
    output.write("Set, Algorithm, Time, PG Vertices, Priorities, Memory (MB), BDD Nodes, Peak Live BDD Nodes, Peak BDD Nodes\n")
    
    #Aggregate csv data
    data = { key : [] for key in benchmarks.values() }
    for line in input_lines[1:]:
        split = line.split(',')

        file_name = split[0]
        found = False
        for prefix in benchmarks.keys():
            if not found and file_name.replace("\"", "").startswith(prefix):
                data[benchmarks[prefix]].append(split)
                found = True

        if not found:
            raise Exception("Could not find collection name for file " + file_name)

    for category in data.keys():
        grp = {}
        for row in data[category]:
            alg = row[1]
            if alg in grp:
                entry = grp[alg]
                # 2-7
                for i in range(2,8):
                    entry[i] += float(row[i]) if '.' in row[i] else int(row[i])
                entry[8] += 1
            else:
                grp[alg] = [ category, alg ] + ([0]*6) + [1]
                for i in range(2,8):
                    grp[alg][i] += float(row[i]) if '.' in row[i] else int(row[i])

        for line in grp.values():
            output.write(", ".join([ str(s) for s in line ]) + "\r\n")

        
