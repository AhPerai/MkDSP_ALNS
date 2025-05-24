#!/usr/bin/python3
import os
import sys
import subprocess
import random

# Get the parameters as command line arguments
configuration_id = sys.argv[1]
instance_id = sys.argv[2]
seed = sys.argv[3]
instance = sys.argv[4]
conf_params = " ".join(sys.argv[5:])
fixed_params = "--k 2 --method iteration --limit 5000"

command = f"../alns_exe -f {instance} {conf_params}"

result = str(subprocess.check_output(command, shell=True))
print(result)
