#!/usr/bin/env bash

'''
This file sets up the virtual environment.
Run "source setup.sh" each time you want to run the app.
'''

# Do the following at the terminal BEFORE running this script:
# sudo apt-get update
# sudo apt-get install python-dev python-pip
# sudo pip3 install --upgrade pip
# sudo apt-get install bluetooth bluez-utils blueman


python3 -m pip install --user virtualenv

# Establish a virtual environment and activate it
if [ ! -d venv ]
then
  python3 -m virtualenv venv
fi

. venv/bin/activate



pip3 install -r requirements.txt

git clone https://github.com/adafruit/Adafruit_CircuitPython_PCA9685

cd Adafruit_CircuitPython_PCA9685

python setup.py install

cd ..

ln -s /usr/local/python/cv2/python-3.7/cv2.cpython-37m-arm-linux-gnueabihf.so venv/lib/python3.7/site-packages/cv2.so
