#!/usr/bin/env bash

'''
This file sets up the virtual environment.
Run "source setup.sh" each time you want to run the app.
'''

pip install virtualenv

# Establish a virtual environment and activate it
if [ ! -d venv ]
then
  virtualenv venv
fi

. venv/bin/activate


#sudo apt-get install python3-pip
#sudo pip3 install --upgrade setuptools

#pip3 install --upgrade pip

pip3 install -r requirements.txt

git clone https://github.com/adafruit/Adafruit_CircuitPython_PCA9685

python Adafruit_CircuitPython_PCA9685/setup.py install
