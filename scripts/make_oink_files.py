import os

KNOR_PATH = "../../knor/"

count = 0
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