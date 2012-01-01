#!/bin/sh

# This is file to be called by launchd
nice -n 20 "$(dirname $0)"/entry.sh --daemon_run
