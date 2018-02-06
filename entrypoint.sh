#!/bin/bash

python3 --version > /dev/null 2>&1 && exec python3 entrypoint.py $@
python2 --version > /dev/null 2>&1 && exec python2 entrypoint.py $@
echo "No python found, exiting."
exit 1
