import os
import subprocess

subprocess.call("iwlist wlan0 scan > temp.txt", shell = True)
output = open("temp.txt")

lines = output.readlines()

for index, line in enumerate(lines):

    if "Address" in line:

        address = line[29:-1]
        name = lines[index + 1].split("\"")[1]

        print "%s is %s" % (address, name)

os.system("rm temp.txt")
