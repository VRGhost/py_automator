#!/bin/sh

cd "$(dirname $0)"

if [ ! -f virtualenv.py ]; then
    wget --no-check-certificate \
        'https://raw.github.com/pypa/virtualenv/master/virtualenv.py'
fi

if [ ! -d ./bin ]; then
    python2.7 ./virtualenv.py .
fi

source ./bin/activate

easy_install tendo
