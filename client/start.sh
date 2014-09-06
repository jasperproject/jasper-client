#!/bin/bash
cd $JASPER_HOME/jasper/client
rm -rf ../old_client
python2 main.py &
