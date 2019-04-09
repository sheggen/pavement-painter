#!/usr/bin/env bash

'''
This file sets up the virtual environment.
Run "source setup.sh" each time you want to run the app.
'''

# Do the following at the terminal BEFORE running this script:
# sudo apt-get update
# sudo apt-get install python-dev python-pip
# sudo pip3 install --upgrade pip


python3 -m pip install --user virtualenv

# Establish a virtual environment and activate it
if [ ! -d venv ]
then
  python3 -m virtualenv venv
fi

. venv/bin/activate

pip3 install -r requirements.txt

git clone https://github.com/adafruit/Adafruit_CircuitPython_PCA9685

python Adafruit_CircuitPython_PCA9685/setup.py install
