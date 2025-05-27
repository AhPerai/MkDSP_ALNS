#!/usr/bin/python3
import sys
import subprocess

# Get the parameters as command line arguments
configuration_id = sys.argv[1]
instance_id = sys.argv[2]
seed = sys.argv[3]
instance_full_path = sys.argv[4]
k_value = sys.argv[5]
conf_params = " ".join(sys.argv[6:])

split_marker = "algorithms"
instance = (
    instance_full_path[instance_full_path.index(split_marker) :]
    if split_marker in instance_full_path
    else instance_full_path
)


command = f"python algorithms/runner/alns/alns_exe.py -f {instance} -k {k_value} {conf_params}"

content = str(subprocess.check_output(command, shell=True))
result = content.split("|")[-1].split(": ")[-1].split("\\")[0]
print(result)
