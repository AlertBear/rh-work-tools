#!/usr/bin/python

import subprocess
import sys

class ExecError(Exception):
    pass
    
def execute(cmd, check=True):
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        if check:
            raise ExecError(e.output)
        else:
            return e.output
    else:
        return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    try:
        output = execute(cmd)
    except ExecError as e:
        print "Not successfully"
    else:
        print output
