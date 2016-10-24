#!/bin/env python

##
# Logs a job start to the process.log file and to screen
##

import os, sys, time

import common

state = "Message"
script = os.getenv('SLURM_JOB_NAME', None)
if len(sys.argv) >= 2:
	state = sys.argv[1]
#fi
if script is None:
	script = sys.argv[2]

# check if its a slurm or interactive job
if os.environ.get('SLURM_JOBID') is not None:
	common.writelog("%s slurm job: %s. Name=%s Nodes=%s" % (
		state,
		os.environ.get('SLURM_JOBID'),
		script,
		os.environ.get('SLURM_JOB_NODELIST'),
	))
else:
	common.writelog("%s interactive job. Name=%s Nodes=%s" % (
		state,
		script,
		os.environ.get('HOSTNAME'),
	))
# fi

print "[%s] %s at: %s" % (
	script,
	state,
	time.strftime("%Y-%m-%d %H:%M:%S"),
)

