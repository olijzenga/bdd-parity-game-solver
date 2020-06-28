import os

KNOR_PATH = "../../knor/"

count = 0
# Ugly script for calling the knor (https://github.com/trolando/knor) binary on all files in the experiments folder of knor.
# A slightly modified version of knor is used which only prints the parity game in pgsolver format to the terminal. So all
# other prints were removed. This results in a clean pgsolver output which we can dump into a file directly.
for file in os.listdir(KNOR_PATH + "examples"):
    print("Found file {0}".format(file))
    if file.endswith(".ehoa"):
        count += 1
        print("Building .oink file for {0}...".format(file))
        cmd = "{0} {1} dfi > {2}".format(KNOR_PATH + "build/knor", KNOR_PATH + "examples/" + file, "../experiments/syntcomp/" + file + ".oink")
        print(cmd)
        os.system(cmd)
        print("Successfully built file {0}!".format(file + ".oink"))
    
print("Build {0} .oink files".format(count))