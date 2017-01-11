#!/usr/bin/python

import sys
import re
from fabric.api import run, env

env.host_string = "root@" + sys.argv[1]
env.password = "redhat"

cmd_pvs = "pvs|grep '/dev'"
output_pvs = run(cmd_pvs)

if output_pvs:
    pvs_split = output_pvs.split()
    for pv in pvs_split:
        if re.search('/dev/', pv):
            cmd = "dd if=/dev/zero of=%s bs=20M count=10" % pv    
            run(cmd)
