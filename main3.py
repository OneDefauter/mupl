import os
import subprocess

path_file = os.path.join(os.path.dirname(__file__), "run.py")

folder_executed = os.getcwd()
command = ['python', path_file, folder_executed]
subprocess.run(command)