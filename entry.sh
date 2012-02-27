#!/bin/sh

cd "$(dirname $0)"
source ./_env/bin/activate
PYTHONPATH="$PYTHONPATH:." python ./osx-rule-actions/run.py $*
