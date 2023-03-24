import subprocess
import sys

vrep_path = '/home/zoker/CoppeliaSim'
# server_port = sys.argv[1]
server_port = '19997'

command1 = "cd {} && ./coppeliaSim.sh -gREMOTEAPISERVERSERVICE_".format(vrep_path) + server_port + "_FALSE_TRUE "

com1 = subprocess.Popen(command1, shell=True)