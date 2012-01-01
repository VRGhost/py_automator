#!/bin/sh

# This is file to be called by launchd
PYTHONPATH=".;$PYTHONPATH" nice -n 20 python $(dirname "$0")/run.py --daemon_run
