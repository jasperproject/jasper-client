#!/bin/bash
if [[ -z "$JASPER_HOME" ]]; then
    if [[ -d "/home/pi" ]]; then
        JASPER_HOME="/home/pi"
        export JASPER_HOME;
    else
        echo "Error: \$JASPER_HOME is not set."
        exit 0;
    fi
fi

cd $JASPER_HOME/jasper/boot
LD_LIBRARY_PATH="/usr/local/lib"
export LD_LIBRARY_PATH
PATH=$PATH:/usr/local/lib/
export PATH
python boot.py &
