#!/bin/sh

pushd `dirname $0` > /dev/null

python guessSettings.py $*

popd > /dev/null
