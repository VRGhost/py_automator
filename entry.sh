#!/bin/sh

cd "$(dirname $0)"
source ./_env/bin/activate
python ./osx-rule-actions/run.py $*
