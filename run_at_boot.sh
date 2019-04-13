#!/usr/bin/env bash

'''
This file runs the pavement printer code. It is intended to run at boot.
'''


# Establish a virtual environment and activate it
if [ ! -d venv ]
then
  python3 -m virtualenv venv
fi

. venv/bin/activate

printf "Starting Pavement Painter Program" > /home/pi/pp_log.txt 2>&1

python /home/pi/pavement-painter/main.py & > /home/pi/pp_log.txt 2>&1
